import pdfparser.poppler as pdf
import sys
import re

MIN_SECTION_HEADER_SIZE = 13
MAX_SECTION_HEADER_SIZE = 14.5

d=pdf.Document(sys.argv[1])

sections = [['',['']]]

last_color = None
last_font_size = None
# print('No of pages', d.no_of_pages)
for p in d:
    # print('Page', p.page_no, 'size =', p.size)
    for f in p:
        # print(' '*1,'Flow')
        for b in f:
            # print(' '*2,'Block', 'bbox=', b.bbox.as_tuple())
            for l in b:
                # print(' '*3, l.text.encode('UTF-8'), '(%0.2f, %0.2f, %0.2f, %0.2f)'% l.bbox.as_tuple())
                #assert l.char_fonts.comp_ratio < 1.0
                for i in range(len(l.text)):
                    # print(l.text[i].encode('UTF-8'), '(%0.2f, %0.2f, %0.2f, %0.2f)'% l.char_bboxes[i].as_tuple(),\
                    #   l.char_fonts[i].name, l.char_fonts[i].size, l.char_fonts[i].color,)
                    if MIN_SECTION_HEADER_SIZE < l.char_fonts[i].size < MAX_SECTION_HEADER_SIZE:
                        sections[-1][0] += l.text[i].encode('UTF-8')
                    elif MIN_SECTION_HEADER_SIZE < last_font_size < MAX_SECTION_HEADER_SIZE:
                        sections.append(['',['']])
                    color = l.char_fonts[i].color
                    # Assume anything not black is highlighted and ergo worth
                    # noting down
                    if color.as_tuple() != (0,0,0):
                       sections[-1][1][-1] += l.text[i].encode('UTF-8')
                    elif last_color != (0,0,0):
                       sections[-1][1].append('')
                    last_color = color.as_tuple()
                    last_font_size = l.char_fonts[i].size

filter_alpha = lambda s: str(filter(lambda c: c not in ',.;:', s))
tidy_spaces = lambda s: ' '.join(s.split())

output = sys.argv[2]
sections = list(filter(lambda s: s[0] or s[1], sections))
with open(output,'w+') as f:
    for section in sections:
        if section[0]:
            for highlight in section[1]:
                s = filter_alpha(tidy_spaces(highlight))
                if s: f.write(s + '\n')
            f.write('\n' + section[0] + '\n')

