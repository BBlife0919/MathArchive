"""CLIP 시각 임베딩으로 시험문제 ↔ 교재문제 매칭.

ViT-B-32 (OpenAI) 사용. MPS 가속.
"""
from __future__ import annotations
import json
import re
from pathlib import Path
import numpy as np
import torch
from PIL import Image
import open_clip

ROOT = Path('/Users/youngwoolee/MathDB/output/textbook_match')
EXAM_DIR = ROOT / 'crops_exam'
TB_DIR = ROOT / 'crops_textbook'

DEVICE = 'mps' if torch.backends.mps.is_available() else 'cpu'
print(f'device: {DEVICE}')


def load_model():
    model, _, preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='openai')
    model.eval()
    model = model.to(DEVICE)
    return model, preprocess


@torch.no_grad()
def embed_images(model, preprocess, image_paths: list[Path], batch_size: int = 64) -> np.ndarray:
    feats = []
    for i in range(0, len(image_paths), batch_size):
        batch = image_paths[i:i + batch_size]
        imgs = []
        for p in batch:
            try:
                img = Image.open(p).convert('RGB')
                imgs.append(preprocess(img))
            except Exception as e:
                print(f'err {p}: {e}')
                imgs.append(torch.zeros(3, 224, 224))
        x = torch.stack(imgs).to(DEVICE)
        f = model.encode_image(x)
        f = f / f.norm(dim=-1, keepdim=True)
        feats.append(f.cpu().numpy())
        if (i // batch_size) % 5 == 0:
            print(f'  embedded {i + len(batch)}/{len(image_paths)}')
    return np.concatenate(feats, axis=0)


def main():
    # 시험문제 이미지 목록
    exam_paths = sorted(EXAM_DIR.glob('*.png'))
    exam_ids = [p.stem for p in exam_paths]
    print(f'exam images: {len(exam_paths)}')

    # 교재 이미지 목록
    tb_paths = sorted(TB_DIR.glob('*.png'))
    tb_codes = [p.stem for p in tb_paths]
    print(f'textbook images: {len(tb_paths)}')

    # 모델 로드
    model, preprocess = load_model()

    print('embedding exam...')
    exam_feats = embed_images(model, preprocess, exam_paths)
    print('embedding textbook...')
    tb_feats = embed_images(model, preprocess, tb_paths)

    # 코사인 유사도 (이미 정규화됨)
    sims = exam_feats @ tb_feats.T  # [62, 1416]
    print(f'sim matrix: {sims.shape}, min={sims.min():.3f}, max={sims.max():.3f}')

    # textbook 메타 로드
    tb_meta = {}
    tb = json.load(open(ROOT / 'textbooks_index.json'))
    for key, info in tb.items():
        for p in info['problems']:
            tb_meta[p['code']] = {
                'tb_key': key,
                'tb_label': info['meta']['label'],
                'tb_short': info['meta']['short'],
                'page': p['page'],
                'text': p['text'],
            }

    # 학교별 매칭 (top 10)
    results: dict[str, list] = {}
    for i, qid in enumerate(exam_ids):
        # qid: '광명고_Q03'
        m = re.match(r'(.+?)_Q(\d+)', qid)
        if not m:
            continue
        school, qno = m.group(1), int(m.group(2))
        sim_row = sims[i]
        # top-10 indices
        top_idx = np.argsort(-sim_row)[:10]
        top = []
        for j in top_idx:
            code = tb_codes[j]
            meta = tb_meta.get(code, {})
            top.append({
                'score': float(sim_row[j]) * 100,  # 0~100 스케일
                'code': code,
                'tb_key': meta.get('tb_key', ''),
                'tb_short': meta.get('tb_short', ''),
                'page': meta.get('page', -1),
                'text_orig': meta.get('text', '')[:300],
            })
        results.setdefault(school, []).append({
            'q_no': qno,
            'qid': qid,
            'top': top,
        })

    # 학교별로 q_no 정렬
    for school in results:
        results[school].sort(key=lambda r: r['q_no'])

    out = ROOT / 'clip_matches.json'
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(f'wrote {out}')

    # 요약
    print('\n=== 요약 ===')
    for school, res in results.items():
        s_high = sum(1 for r in res if r['top'][0]['score'] >= 88)
        s_mid = sum(1 for r in res if 80 <= r['top'][0]['score'] < 88)
        s_low = len(res) - s_high - s_mid
        print(f'{school}: 고매칭 {s_high}, 중매칭 {s_mid}, 저매칭 {s_low}')


if __name__ == '__main__':
    main()
