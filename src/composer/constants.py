"""
Constants and Fluent UI styles for Microsoft Teams messages.
"""

DOC_LINKS = {
    "xu_ly_phan_hoi": "https://docs.google.com/document/d/1eptdDdXD1e1Tz2xzR0kKgB_uNeAurwhKHB8b-1yUf9I/edit?tab=t.rteda6ijpm46",
    "nop_jobs": "https://docs.google.com/spreadsheets/d/1vUcKAbDazlC_vFSjzty02Fdugu4Nw_jZsEG2k_wyxXY/edit?gid=1653216804#gid=1653216804",
    "willing_job": "https://docs.google.com/document/d/1v15KFMxfk2v3eYyQOiJbL4sCE6RQa3Nuses_cxLnkzM/edit?tab=t.atun0hlffezr#heading=h.gpe024pkb62i",
    "interview": "https://docs.google.com/document/d/1phoQJ7SWn8gEGsXq79afmuK8H5JCdsyzaPn_-H4PYBg/edit?tab=t.epjtewsrdzv4",
    "feedback_job": "https://docs.google.com/document/d/1phoQJ7SWn8gEGsXq79afmuK8H5JCdsyzaPn_-H4PYBg/edit?tab=t.43t5jivli07x",
    "ah": "https://docs.google.com/document/d/1JrZHfVV9GHnETvcLrN0GLvHKhp8O3N0efkV49wXyOjY/edit?tab=t.0#heading=h.cr5o8ciz9sfm",
    "au": "https://docs.google.com/document/d/1muhs3g6cpgDTXyUtC9902AfjwYXM_M_Lhi6wJxyCEPo/edit?tab=t.a8v2tuy7i94k",
    "sam_foundation": "https://docs.google.com/document/d/1uTXqOXJ7I8kiYz-0d6YuFLNBJUxwyr4gfRN_rHo1V4c/edit?usp=sharing",
    "niw_citations": "https://docs.google.com/spreadsheets/d/1tV1h-pNtGBgq639ky7cdBjc3CTfoeJEKIakOjORePEM/edit?gid=1346338716#gid=1346338716",
    "niw_notes": "https://docs.google.com/document/d/1__q1kkUZkmpXi1E5dDkbwzfir-HKTCQSYEU4Edz38k0/edit?tab=t.boxu2wiwp4xz#heading=h.j84em85ufx8",
    "niw_linkedin": "https://docs.google.com/spreadsheets/d/163Ye0HpfriaBs7nPWpKZC5mY-nHgcZdIQh2sJMoDIuQ/edit?gid=1498442053#gid=1498442053",
    "niw_case": "https://docs.google.com/document/d/1__q1kkUZkmpXi1E5dDkbwzfir-HKTCQSYEU4Edz38k0/edit?tab=t.boxu2wiwp4xz"
}

LINK_CLS = (
    'class="fui-Link ___1q1shib f2hkw1w f3rmtva f1ewtqcl fyind8e f1k6fduh f1w7gpdv '
    'fk6fouc fjoy568 figsok6 f1s184ao f1mk8lai fnbmjn9 f1o700av f13mvf36 f1cmlufx '
    'f9n3di6 f1ids18y f1tx3yz7 f1deo86v f1eh06m1 f1iescvh fhgqx19 f1olyrje f1p93eir '
    'f1nev41a f1h8hb77 f1lqvz6u f10aw75t fsle3fq f17ae5zn"'
)

LINK_ATTRS = (
    f'{LINK_CLS} rel="noopener noreferrer" target="_blank" tabindex="0" data-testid="atp-safelink"'
)

# Highlight Styles chuẩn Microsoft Teams (Sử dụng mã màu bảng màu gốc Teams palette để CKEditor không bị lọc mất)
BLUE_STYLE = 'style="color: rgb(30, 83, 163);"'

# Màu đỏ/cam chuẩn của Ray trong nhóm gbBOSS (Teams tự động chuyển sang rgb(254, 131, 93) khi ở Dark Mode)
RED_STYLE = 'style="color: rgb(205, 89, 55);"'
ORANGE_STYLE = RED_STYLE

