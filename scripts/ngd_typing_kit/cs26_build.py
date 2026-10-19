# -*- coding: utf-8 -*-
"""철산중3 기말대비 프린트 HWPX 조립기(build.py 재사용).
쪽별 내용 모듈(cs26_content=1쪽, cs26_p02_content ... )의 Q를 이어붙여 한 파일로 만든다.
  최종본: python3 cs26_build.py all            -> ~/Downloads/철산중3 기말대비 프린트 이영우T.hwpx
  쪽 시험: python3 cs26_build.py p02 [p03 ...]  -> ./out/cs26_test_<쪽>.hwpx (Downloads에 쓰지 않음)
그림 먼저: cd figures && python3 cs26_pXX_figs.py
"""
import os, sys, importlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as B

ALL = ['cs26_content'] + [f'cs26_p{n:02d}_content' for n in (2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21)]


def load(names):
    Q = []
    for n in names:
        try:
            m = importlib.import_module(n)
        except ModuleNotFoundError as e:
            if e.name == n:
                print('SKIP(없음)', n)
                continue
            raise
        Q += m.Q
    ids = [q['id'] for q in Q]
    assert len(ids) == len(set(ids)), 'id 중복'
    return Q


B.MAX_PER = 3
B.COL_USABLE = 77000
B.IDS.z = 1000
B.SCHOOL_TITLE = '철산중3 기말대비 프린트'
B.SCHOOL = '이영우T'
B.COURSE = '수학'
B.UNITS = '원의 성질 ~ 통계'
B.PROD_DATE = '2026년 10월 19일'
B.DOC_TITLE = '철산중3 기말대비 프린트 이영우T'

if __name__ == '__main__':
    args = sys.argv[1:] or ['all']
    if args == ['all']:
        B.Q = load(ALL)
        B.OUTDIR = '/Users/youngwoolee/Downloads'
        B.FILENAME_STEM = '철산중3 기말대비 프린트 이영우T'
    else:
        names = ['cs26_content' if a == 'p01' else f'cs26_{a}_content' for a in args]
        B.Q = load(names)
        B.OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
        os.makedirs(B.OUTDIR, exist_ok=True)
        B.FILENAME_STEM = 'cs26_test_' + '_'.join(args)
    p, warns, info = B.build()
    print(p, '문항수', len(B.Q))
    for w in warns:
        print('WARN', w)
    for g in info:
        print(g)
