#!/usr/bin/env python3
"""Attribute public dialogue units to speakers by voice. Local-only: it needs the audio archive.

Stages write under --work and reuse what is already there, so a run can stop and resume:

  embed  one speaker embedding per subtitle cue, with pyannote/wespeaker-voxceleb-resnet34-LM from
         the local model cache, for every structured dialogue and every solo talk with local audio.
  label  Yuzheng's voice profile from the solo talks; then for each dialogue his in-video voice from
         the cues closest to the profile, the other voices among cues clearly unlike him, and a
         label per cue only where the profile and the voices of that recording agree by a margin.
  acts   the speech act of every attributed unit, by deepseek-v4-flash on AI Builder
         (AI_BUILDER_TOKEN in the environment).
  apply  write the labels into corpus/dialogues/, record the method, thresholds and per-programme
         hashes in config/audio-speaker-policy.json, and rebind both in
         config/public-dialogue-policy.json. Run validate_release.py --write-manifest afterwards.

The profile vector stays in --work: it is a voiceprint, so the policy records only its hash.
embed and label need numpy, scikit-learn, torch, pyannote.audio and ffmpeg; apply needs none.
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import random
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import raw_turn_policy as turns  # noqa: E402

DIALOGUES = "corpus/dialogues"
PUBLIC_POLICY = "config/public-dialogue-policy.json"
MODEL = "pyannote/wespeaker-voxceleb-resnet34-LM"
SR = 16000
AUDIO_EXT = (".m4a", ".mp3", ".opus", ".webm", ".wav", ".aac", ".mp4")
CUE = re.compile(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)")

# Cue embeddings: centre crops of 1.0–6.0 s in 0.5 s steps, so a batch never needs padding.
MIN_CUE_SEC = 1.0
MIN_CLUSTER_SEC = 1.5
# Similarity to Yuzheng's cross-session profile at the cue level. Solo talks: 5th percentile ≈ 0.6.
SEED_TIERS = [("strict", 0.68, 60.0, 10), ("medium", 0.64, 30.0, 8), ("loose", 0.62, 15.0, 6)]
SEED_OTHER = 0.45
LABEL_Y_MIN = 0.55
LABEL_G_MAX = 0.50
MARGIN = 0.10
OWN_MIN = 0.40
OTHER_THRESHOLD = 0.55
MIN_VOICE_SEC = 45.0
THRESHOLDS = {
    "cue_seconds": {"labelled_at_least": MIN_CUE_SEC, "voices_found_from_at_least": MIN_CLUSTER_SEC},
    "yuzheng_seed_tiers": [{"name": n, "profile_similarity_at_least": t, "speech_seconds_at_least": s, "cues_at_least": c}
                           for n, t, s, c in SEED_TIERS],
    "other_voice_seed_profile_similarity_at_most": SEED_OTHER,
    "yuzheng_label_profile_similarity_at_least": LABEL_Y_MIN,
    "guest_label_profile_similarity_at_most": LABEL_G_MAX,
    "nearest_voice_margin_at_least": MARGIN,
    "nearest_voice_similarity_at_least": OWN_MIN,
    "other_voice_clustering": {"linkage": "average", "metric": "cosine", "distance_threshold": OTHER_THRESHOLD},
    "guest_named_when": "the catalog lists exactly one person for the programme and exactly one other voice was found",
}
ACT_CODES = {"S": "statement", "Q": "question", "I": "introduction", "A": "acknowledgement", "J": "joke", "R": "reported-other"}
ACT_MODEL = "deepseek-v4-flash"
ACT_URL = "https://space.ai-builders.com/backend/v1/chat/completions"
ACT_PROMPT = """你在给中文播客对谈的逐句字幕标注“言语行为”。每行格式：编号|说话人|字幕。说话人是“立正”（主持人）、“嘉宾”或“未定”。
只给说话人是“立正”或“嘉宾”的行打标签，“未定”的行只作上下文，不要输出。标签：
S＝陈述：说话人自己的观点、经历、事实或解释。
Q＝提问：任何问句，包括追问、反问、请对方展开、确认式提问（“是不是……”“对吧？”），以及为提问做铺垫的半句。
I＝介绍：节目开场白（含开头介绍本期话题、回顾以前的节目）、介绍嘉宾、嘉宾的自我介绍（姓名、学历、工作经历的履历式介绍）、说明节目流程、结尾感谢收看。
A＝回应：只是附和或回应（对、嗯、是的、哈哈、有道理、明白、好的），没有实质内容。
J＝玩笑：明显的玩笑、调侃、反讽，包括说话人自己说“开玩笑”的那几句。
R＝转述：复述别人说的话或别人的观点（“他说……”“有人觉得……”“你刚才说……”），说话人自己并不主张。
一句话被字幕切成几行时，按整句的作用给每行打同样的标签。只有明确是说话人自己在陈述时才标S；拿不准是陈述还是提问、转述时，选Q或R。
输出JSON对象：{"labels": {"编号": "标签", ...}}，覆盖所有“立正”和“嘉宾”的行，不要其他内容。"""


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value, indent=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=indent) + ("\n" if indent else ""), encoding="utf-8")


# ---------------------------------------------------------------- audio and embeddings

def audio_map(archive: Path) -> dict[str, list[str]]:
    """Video id -> audio files: any archive folder named <id> or ending in _<id>."""
    found: dict[str, list[str]] = {}
    for folder, _dirs, names in os.walk(archive):
        base = os.path.basename(folder)
        m = re.search(r"_([A-Za-z0-9_-]{11})$", base)
        vid = m.group(1) if m else (base if re.fullmatch(r"[A-Za-z0-9_-]{11}", base) else None)
        if not vid:
            continue
        for name in sorted(names):
            path = os.path.join(folder, name)
            if name.lower().endswith(AUDIO_EXT) and os.path.getsize(path) > 10000:
                found.setdefault(vid, []).append(path)
    return found


def pick_audio(files: list[str]) -> str | None:
    for rule in (lambda f: f.endswith(".source-refreshed.m4a"), lambda f: "/会员视频/" not in f and f.endswith(".m4a"),
                 lambda f: f.endswith(".m4a"), lambda f: True):
        hit = [f for f in files if rule(f)]
        if hit:
            return hit[0]
    return None


def decode(path: str):
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def subtitle_cues(path: Path) -> list[tuple[float, float]]:
    cues = []
    for m in CUE.finditer(path.read_text(errors="ignore")):
        h1, m1, s1, f1, h2, m2, s2, f2 = m.groups()
        a = int(h1) * 3600 + int(m1) * 60 + int(s1) + int(f1) / 10 ** len(f1)
        b = int(h2) * 3600 + int(m2) * 60 + int(s2) + int(f2) / 10 ** len(f2)
        if b > a:
            cues.append((a, b))
    return cues


def solo_cues(archive: Path, vid: str, audio: str) -> list[tuple[float, float]]:
    """A solo talk's speech, from its archive subtitles; long cues are cut into 4 s windows."""
    folder = Path(audio).parent
    candidates = [p for pattern in ("*.qwen.srt", "*.zh-Hans.srt", "*.zh.srt", "*.zh-CN.srt", "*.srt") for p in sorted(folder.glob(pattern))]
    member = archive / "会员字幕" / vid / "transcript.srt"
    candidates += [member] if member.exists() else []
    for path in dict.fromkeys(candidates):
        cues = subtitle_cues(path)
        if len(cues) >= 5:
            out = []
            for a, b in cues:
                t = a
                while b - t >= MIN_CLUSTER_SEC:
                    out.append((t, min(b, t + 6.0) if b - a <= 8.0 else min(b, t + 4.0)))
                    t = out[-1][1]
            return out
    return []


class Embedder:
    def __init__(self, batch: int = 96):
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
        import torch
        from pyannote.audio import Model
        self.torch = torch
        self.device = torch.device("mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu"))
        self.model = Model.from_pretrained(MODEL).to(self.device).eval()
        self.batch = batch

    def embed(self, wave, segments):
        import numpy as np
        out = np.full((len(segments), 256), np.nan, dtype=np.float32)
        buckets: dict[float, list[tuple[int, int]]] = {}
        for i, (a, b) in enumerate(segments):
            if b - a < MIN_CUE_SEC:
                continue
            length = min(6.0, np.floor((b - a) / 0.5) * 0.5)
            n = int(round(length * SR))
            start = max(0, min(int(round((a + b) / 2 * SR)) - n // 2, len(wave) - n))
            if start + n <= len(wave):
                buckets.setdefault(length, []).append((i, start))
        with self.torch.inference_mode():
            for length, items in buckets.items():
                n = int(round(length * SR))
                for k in range(0, len(items), self.batch):
                    chunk = items[k:k + self.batch]
                    x = np.stack([wave[s:s + n] for _, s in chunk])[:, None, :]
                    emb = self.model(self.torch.from_numpy(x).to(self.device)).float().cpu().numpy()
                    emb /= np.linalg.norm(emb, axis=1, keepdims=True) + 1e-9
                    for (i, _), e in zip(chunk, emb):
                        out[i] = e
        return out


def solo_ids(root: Path) -> list[str]:
    rows = [json.loads(line) for line in (root / "catalog/videos.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    return sorted(r["video_id"] for r in rows if r.get("speaker_classification") == "solo-yuzheng")


def stage_embed(root: Path, archive: Path, work: Path, only: list[str] | None):
    import numpy as np
    files = audio_map(archive)
    embedder = Embedder()
    jobs = [(path.stem.removeprefix("youtube-"), "dialogue") for path in sorted((root / DIALOGUES).glob("youtube-*.json"))]
    jobs += [(vid, "solo") for vid in solo_ids(root)]
    for vid, kind in jobs:
        target = work / "emb" / f"{vid}.npz"
        if (only and vid not in only) or target.exists():
            continue
        audio = pick_audio(files.get(vid, []))
        if not audio:
            print(vid, "no local audio", flush=True)
            continue
        if kind == "dialogue":
            segments = [(u["start_seconds"], u["end_seconds"]) for u in read_json(root / DIALOGUES / f"youtube-{vid}.json")["units"]]
        else:
            segments = solo_cues(archive, vid, audio)
        if not segments:
            print(vid, "no subtitles", flush=True)
            continue
        wave = decode(audio)
        X = embedder.embed(wave, segments)
        target.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(target, X=X.astype(np.float16), segs=np.array(segments, dtype=np.float32), kind=kind,
                            audio=audio, audio_sha256=sha256_bytes(Path(audio).read_bytes()), duration=len(wave) / SR)
        print(vid, kind, len(segments), flush=True)


# ---------------------------------------------------------------- labelling

@dataclass
class Recording:
    X: object
    segs: object
    audio_sha256: str

    @property
    def dur(self):
        return self.segs[:, 1] - self.segs[:, 0]

    @property
    def valid(self):
        import numpy as np
        return ~np.isnan(self.X[:, 0])


def load_recording(work: Path, vid: str) -> Recording | None:
    import numpy as np
    path = work / "emb" / f"{vid}.npz"
    if not path.exists():
        return None
    z = np.load(path, allow_pickle=False)
    digest = str(z["audio_sha256"]) if "audio_sha256" in z.files else sha256_bytes(Path(str(z["audio"])).read_bytes())
    return Recording(z["X"].astype(np.float32), z["segs"], digest)


def unit_vector(v):
    import numpy as np
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-9)


def robust_centroid(Z, keep=0.6, rounds=4):
    import numpy as np
    c = unit_vector(Z.mean(0))
    for _ in range(rounds):
        s = Z @ c
        c = unit_vector(Z[s >= np.quantile(s, 1 - keep)].mean(0))
    return c


def build_profile(root: Path, work: Path):
    """His voice across sessions: the consensus of each solo talk's dominant voice."""
    import numpy as np
    centres = []
    for vid in solo_ids(root):
        r = load_recording(work, vid)
        if r is None:
            continue
        m = r.valid & (r.dur >= MIN_CLUSTER_SEC)
        if m.sum() >= 30:
            centres.append(robust_centroid(r.X[m]))
    P = robust_centroid(np.stack(centres), keep=0.7)
    return P, len(centres)


@dataclass
class Labels:
    state: str
    labels: list
    voices: dict = field(default_factory=dict)
    tier: str | None = None


def label_recording(r: Recording, P, force_yuzheng=None) -> Labels:
    """Per cue: ("yuzheng"|"other:<j>", margin) or None. force_yuzheng is a confirmed in-video voice."""
    import numpy as np
    from sklearn.cluster import AgglomerativeClustering
    ok = r.valid & (r.dur >= MIN_CUE_SEC)
    longc = r.valid & (r.dur >= MIN_CLUSTER_SEC)
    s = np.where(r.valid, r.X @ P, np.nan)
    Y, tier = force_yuzheng, ("maintainer-confirmed" if force_yuzheng is not None else None)
    if Y is None:
        for name, threshold, min_sec, min_cues in SEED_TIERS:
            seed = np.where(longc & (s >= threshold))[0]
            if r.dur[seed].sum() >= min_sec and len(seed) >= min_cues:
                Y, tier = robust_centroid(r.X[seed], keep=0.8), name
                break
    cand = longc & (s <= SEED_OTHER)
    if Y is not None:
        cand &= (r.X @ Y) <= 0.45
    idx = np.where(cand)[0]
    others = []
    if len(idx) >= 8:
        if len(idx) > 1500:
            idx = idx[np.linspace(0, len(idx) - 1, 1500).astype(int)]
        agg = AgglomerativeClustering(n_clusters=None, metric="cosine", linkage="average", distance_threshold=OTHER_THRESHOLD).fit(r.X[idx])
        secs = np.bincount(agg.labels_, weights=r.dur[idx])
        for k in np.argsort(-secs):
            if secs[k] >= MIN_VOICE_SEC * 0.5:
                c = unit_vector(r.X[idx][agg.labels_ == k].mean(0))
                if all(float(c @ o) < 0.6 for o in others):
                    others.append(c)
    centres = ([Y] if Y is not None else []) + others
    labels = [None] * len(r.X)
    if not centres:
        return Labels("too-little-speech", labels)
    S = r.X @ np.stack(centres).T
    offset = 1 if Y is not None else 0
    seconds: dict[str, float] = {}
    for i in np.where(ok)[0]:
        sims = S[i]
        k = int(np.argmax(sims))
        second = float(np.sort(sims)[-2]) if len(sims) > 1 else 0.0
        margin = float(sims[k] - second)
        if margin < MARGIN or sims[k] < OWN_MIN:
            continue
        if Y is not None and k == 0:
            if force_yuzheng is not None or s[i] >= LABEL_Y_MIN:
                labels[i] = ("yuzheng", round(margin, 3))
        elif s[i] <= LABEL_G_MAX:
            labels[i] = (f"other:{k - offset}", round(margin, 3))
        if labels[i]:
            seconds[labels[i][0]] = seconds.get(labels[i][0], 0.0) + float(r.dur[i])
    voices = {key: round(sec, 1) for key, sec in seconds.items() if key == "yuzheng" or sec >= MIN_VOICE_SEC}
    labels = [lab if lab and lab[0] in voices else None for lab in labels]
    if Y is None:
        state = "yuzheng-absent" if np.nanmean(s[ok] >= 0.62) < 0.05 else "uncertain"
    else:
        state = "yuzheng-found"
    return Labels(state, labels, voices, tier)


def stage_label(root: Path, work: Path, only: list[str] | None, confirmed: dict):
    import numpy as np
    profile_path = work / "profile.npy"
    if profile_path.exists():
        P = np.load(profile_path)
    else:
        P, count = build_profile(root, work)
        np.save(profile_path, P)
        write_json(work / "profile.json", {"solo_talks": count})
    summary = {}
    for path in sorted((root / DIALOGUES).glob("youtube-*.json")):
        vid = path.stem.removeprefix("youtube-")
        if only and vid not in only:
            continue
        r = load_recording(work, vid)
        if r is None:
            continue
        force = None
        if vid in confirmed and confirmed[vid].get("yuzheng_seconds"):
            # A confirmed voice: the cues at the times the maintainer heard as Yuzheng seed his voice.
            times = confirmed[vid]["yuzheng_seconds"]
            hits = [i for i, (a, b) in enumerate(r.segs) for t in times if a - 0.5 <= t <= b + 0.5 and r.valid[i]]
            if hits:
                force = robust_centroid(r.X[sorted(set(hits))], keep=1.0, rounds=0)
        result = label_recording(r, P, force)
        write_json(work / "labels" / f"{vid}.json", {"video_id": vid, "state": result.state, "tier": result.tier,
                                                    "voices": result.voices, "audio_sha256": r.audio_sha256, "labels": result.labels})
        summary[vid] = {"state": result.state, "tier": result.tier, "voices": result.voices}
        print(vid, result.state, result.tier, result.voices, flush=True)
    write_json(work / "label-summary.json", summary, indent=1)


# ---------------------------------------------------------------- speech acts

async def classify_window(client, token, units, labels, part, sem):
    def speaker(label):
        return "未定" if not label else ("立正" if label[0] == "yuzheng" else "嘉宾")
    lines = [f"{i}|{speaker(labels[i])}|{units[i]['text'].strip()[:160]}" for i in part]
    want = {str(i) for i in part if labels[i]}
    payload = {"model": ACT_MODEL, "temperature": 0, "max_tokens": 3000, "response_format": {"type": "json_object"},
               "thinking": {"type": "enabled"}, "reasoning_effort": "low",
               "messages": [{"role": "system", "content": ACT_PROMPT}, {"role": "user", "content": "\n".join(lines)}]}
    last = None
    for attempt in range(5):
        async with sem:
            try:
                response = await client.post(ACT_URL, json=payload, headers={"Authorization": "Bearer " + token}, timeout=120)
                if response.status_code == 429 or response.status_code >= 500:
                    raise RuntimeError(f"http {response.status_code}")
                response.raise_for_status()
                got = json.loads(response.json()["choices"][0]["message"]["content"]).get("labels", {})
                out = {k: ACT_CODES[v] for k, v in got.items() if k in want and v in ACT_CODES}
                if len(out) >= 0.9 * len(want):
                    return out
                raise RuntimeError(f"coverage {len(out)}/{len(want)}")
            except Exception as error:  # retried with backoff, then the window stays unlabelled
                last = error
        await asyncio.sleep(2 ** attempt + random.random())
    print("window failed", part[0], last, flush=True)
    return {}


def stage_acts(root: Path, work: Path, only: list[str] | None, concurrency: int):
    import httpx
    token = os.environ.get("AI_BUILDER_TOKEN")
    if not token:
        raise SystemExit("AI_BUILDER_TOKEN is not set")

    async def run():
        sem = asyncio.Semaphore(concurrency)
        async with httpx.AsyncClient() as client:
            for path in sorted((work / "labels").glob("*.json")):
                vid = path.stem
                target = work / "acts" / f"{vid}.json"
                if (only and vid not in only) or target.exists():
                    continue
                units = read_json(root / DIALOGUES / f"youtube-{vid}.json")["units"]
                labels = [tuple(x) if x else None for x in read_json(path)["labels"]]
                parts = [list(range(a, min(len(units), a + 70))) for a in range(0, len(units), 70)]
                parts = [p for p in parts if any(labels[i] for i in p)]
                acts = {}
                for chunk in await asyncio.gather(*(classify_window(client, token, units, labels, p, sem) for p in parts)):
                    acts.update(chunk)
                write_json(target, {"video_id": vid, "model": ACT_MODEL, "acts": acts})
                print(vid, len(acts), flush=True)
    asyncio.run(run())


# ---------------------------------------------------------------- apply

def catalog_people(root: Path) -> tuple[dict, dict]:
    catalog = read_json(root / "catalog/guests.json")
    entities = {e["entity_id"]: e for e in catalog["entities"]}
    people: dict[str, list[str]] = {}
    for row in catalog["appearances"]:
        people.setdefault(row["source_id"], []).append(row["entity_id"])
    return entities, people


def attributed_units(units: list[dict], labels: list, acts: dict, guest: dict | None) -> list[dict]:
    """The dialogue's units with voice labels applied. Reviewed units are kept as they are; an
    other voice is named only when it is the programme's one listed person; a unit without a
    classified speech act stays unresolved."""
    out = []
    for i, unit in enumerate(units):
        unit = dict(unit)
        label = labels[i] if i < len(labels) else None
        act = acts.get(str(i))
        if unit.get("speaker_status") == turns.REVIEWED or not label or act not in turns.ACTS:
            out.append(unit)
            continue
        if label[0] == "yuzheng":
            unit.update(speaker_id="yuzheng", speaker_name="立正", speaker_status=turns.VOICE, speech_act=act)
        elif guest is not None and label[0] == guest["voice"]:
            unit.update(speaker_id=guest["entity_id"], speaker_name=guest["name"], speaker_status=turns.VOICE, speech_act=act)
        out.append(unit)
    return out


def single_guest(labels_file: dict, people: list[str], entities: dict) -> dict | None:
    others = [key for key in labels_file.get("voices", {}) if key.startswith("other:")]
    persons = [e for e in people if entities.get(e, {}).get("entity_type") in {"person", "anonymous-label", "virtual-character"}]
    if len(others) == 1 and len(people) == 1 and len(persons) == 1:
        return {"voice": others[0], "entity_id": persons[0], "name": entities[persons[0]]["display_name"]}
    return None


def stage_apply(root: Path, work: Path, meta: dict, checks: dict):
    entities, people = catalog_people(root)
    public = read_json(root / PUBLIC_POLICY)
    rows = {row["video_id"]: row for row in public["records"] if row.get("video_id")}
    records = []
    for path in sorted((root / DIALOGUES).glob("*.json")):
        vid = path.stem.removeprefix("youtube-")
        if vid not in rows:
            continue
        labels_path, acts_path = work / "labels" / f"{vid}.json", work / "acts" / f"{vid}.json"
        data = read_json(path)
        # Start from the transcript itself: earlier voice labels are cleared before new ones apply.
        units = [u if u.get("speaker_status") != turns.VOICE else
                 {k: v for k, v in u.items() if k != "speech_act"} | {"speaker_id": "unknown", "speaker_name": "", "speaker_status": "unresolved"}
                 for u in data["units"]]
        if labels_path.exists() and acts_path.exists() and vid not in checks.get("withheld", []):
            labels_file = read_json(labels_path)
            guest = single_guest(labels_file, people.get(f"youtube-{vid}", []), entities)
            units = attributed_units(units, labels_file["labels"], read_json(acts_path)["acts"], guest)
            labelled = [u for u in units if u.get("speaker_status") == turns.VOICE]
            if labelled:
                records.append({
                    "video_id": vid, "unknown_units_sha256": turns.digest(turns.unknown_units(units)),
                    "labels_sha256": turns.digest(turns.voice_labels(units)), "audio_sha256": labels_file["audio_sha256"],
                    "counts": {"yuzheng": sum(u["speaker_id"] == "yuzheng" for u in labelled),
                               "guest": sum(u["speaker_id"] != "yuzheng" for u in labelled),
                               "unresolved": sum(u["speaker_id"] == "unknown" for u in units)},
                    "maintainer_check": checks.get("confirmed", {}).get(vid)})
        data["units"] = units
        raw = (json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()
        if raw != path.read_bytes():
            path.write_bytes(raw)
        rows[vid]["sha256"] = sha256_bytes(raw)
    policy = {"schema_version": 1, "method": turns.VOICE_METHOD, "human_audio_review": False, "full_precision_certified": False,
              **meta, "records": records}
    write_json(root / turns.VOICE_POLICY, policy, indent=2)
    public["audio_attribution_policy"] = {"path": turns.VOICE_POLICY, "sha256": sha256_bytes((root / turns.VOICE_POLICY).read_bytes())}
    write_json(root / PUBLIC_POLICY, public, indent=2)
    print(json.dumps({"programmes": len(records), "yuzheng_units": sum(r["counts"]["yuzheng"] for r in records),
                      "guest_units": sum(r["counts"]["guest"] for r in records)}, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("stage", choices=["embed", "label", "acts", "apply"])
    parser.add_argument("--work", type=Path, required=True, help="working folder for embeddings, labels and speech acts")
    parser.add_argument("--archive", type=Path, help="the channel's local audio archive (embed)")
    parser.add_argument("--meta", type=Path, help="apply: JSON with model, profile, thresholds, speech_acts and evaluation")
    parser.add_argument("--checks", type=Path, help="label/apply: maintainer answers (confirmed voices, withheld programmes)")
    parser.add_argument("--videos", nargs="*", help="limit to these video ids")
    parser.add_argument("--concurrency", type=int, default=4)
    args = parser.parse_args()
    checks = read_json(args.checks) if args.checks else {}
    if args.stage == "embed":
        stage_embed(ROOT, args.archive, args.work, args.videos)
    elif args.stage == "label":
        stage_label(ROOT, args.work, args.videos, checks.get("confirmed_voices", {}))
    elif args.stage == "acts":
        stage_acts(ROOT, args.work, args.videos, args.concurrency)
    else:
        meta = read_json(args.meta)
        meta.setdefault("thresholds", THRESHOLDS)
        stage_apply(ROOT, args.work, meta, checks)


if __name__ == "__main__":
    main()
