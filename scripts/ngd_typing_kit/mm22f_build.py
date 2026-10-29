# -*- coding: utf-8 -*-
"""명문고등학교 2학년 2022 1학기 기말 대수(수학1) HWPX 조립기."""
import build as B
from mm22f_content import Q

B.Q = Q
B.SCHOOL_TITLE = '2022년 1학기 기말'
B.SCHOOL = '명문고등학교'
B.COURSE = '대수'
B.UNITS = '일반각과 호도법 ~ 수학적 귀납법'
B.PROD_DATE = '2026년 10월 27일'
B.FILENAME_STEM = '[고][2022][2-1-b][경기광명시][명문고][대수][일반각과호도법-수학적귀납법][그림3-1-3-1]'
B.DOC_TITLE = '2022년 1학기 기말 명문고등학교 2학년 일반각과호도법~수학적귀납법'


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
