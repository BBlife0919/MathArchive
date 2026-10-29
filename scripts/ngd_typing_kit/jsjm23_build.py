# -*- coding: utf-8 -*-
"""진성고등학교 2학년 2023 2학기 중간 수학2 HWPX 조립기."""
import build as B
from jsjm23_content import Q

B.Q = Q
B.SCHOOL_TITLE = '2023년 2학기 중간'
B.SCHOOL = '진성고등학교'
B.COURSE = '수학2'
B.UNITS = '함수의 극한 ~ 함수의 증가와 감소'
B.PROD_DATE = '2026년 10월 28일'
B.FILENAME_STEM = '[고][2023][2-2-a][경기광명시][진성고][수학2][함수의극한-함수의증가와감소][그림2-1-2-1]'
B.DOC_TITLE = '2023년 2학기 중간 진성고등학교 2학년 함수의극한~함수의증가와감소'


def fix_creator(path):
    import zipfile, os
    z = zipfile.ZipFile(path)
    infos = z.infolist()
    data = {i.filename: z.read(i.filename) for i in infos}
    z.close()
    xml = data['Contents/section0.xml'].decode('utf-8')
    xml2 = xml.replace('(2) 제작자 : by N.G.D 수학적 실험 (daum cafe)', '(2) 제작자 : 이영우')
    if xml2 == xml:
        return False
    data['Contents/section0.xml'] = xml2.encode('utf-8')
    tmp = path + '.tmp_creatorfix'
    with zipfile.ZipFile(tmp, 'w') as zo:
        for i in infos:
            comp = zipfile.ZIP_STORED if i.filename == 'mimetype' else zipfile.ZIP_DEFLATED
            zo.writestr(i.filename, data[i.filename], compress_type=comp)
    os.replace(tmp, path)
    return True


if __name__ == '__main__':
    p, warns, info = B.build()
    fixed = fix_creator(p)
    print(p, '| creator_fixed:', fixed)
    for w in warns:
        print('WARN', w)
    for g in info:
        print(g)
