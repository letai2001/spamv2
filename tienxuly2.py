import pandas as pd
import regex as re
# import re
import unicodedata
from pyvi import ViTokenizer
import uuid

bang_nguyen_am = [['a', 'à', 'á', 'ả', 'ã', 'ạ', 'a'],
                  ['ă', 'ằ', 'ắ', 'ẳ', 'ẵ', 'ặ', 'aw'],
                  ['â', 'ầ', 'ấ', 'ẩ', 'ẫ', 'ậ', 'aa'],
                  ['e', 'è', 'é', 'ẻ', 'ẽ', 'ẹ', 'e'],
                  ['ê', 'ề', 'ế', 'ể', 'ễ', 'ệ', 'ee'],
                  ['i', 'ì', 'í', 'ỉ', 'ĩ', 'ị', 'i'],
                  ['o', 'ò', 'ó', 'ỏ', 'õ', 'ọ', 'o'],
                  ['ô', 'ồ', 'ố', 'ổ', 'ỗ', 'ộ', 'oo'],
                  ['ơ', 'ờ', 'ớ', 'ở', 'ỡ', 'ợ', 'ow'],
                  ['u', 'ù', 'ú', 'ủ', 'ũ', 'ụ', 'u'],
                  ['ư', 'ừ', 'ứ', 'ử', 'ữ', 'ự', 'uw'],
                  ['y', 'ỳ', 'ý', 'ỷ', 'ỹ', 'ỵ', 'y']]

bang_ky_tu_dau = ['', 'f', 's', 'r', 'x', 'j']
nguyen_am_to_ids = {}

for i in range(len(bang_nguyen_am)):
    for j in range(len(bang_nguyen_am[i]) - 1):
        nguyen_am_to_ids[bang_nguyen_am[i][j]] = (i, j)

def chuan_hoa_unicode(text):
    text = unicodedata.normalize('NFC', text)
    return text

def chuan_hoa_dau_tu_tieng_viet(word):
    if not is_valid_vietnam_word(word):
        return word
 
    chars = list(word)
    dau_cau = 0
    nguyen_am_index = []
    qu_or_gi = False
    for index, char in enumerate(chars):
        x, y = nguyen_am_to_ids.get(char, (-1, -1))
        if x == -1:
            continue
        elif x == 9:  # check qu
            if index != 0 and chars[index - 1] == 'q':
                chars[index] = 'u'
                qu_or_gi = True
        elif x == 5:  # check gi
            if index != 0 and chars[index - 1] == 'g':
                chars[index] = 'i'
                qu_or_gi = True
        if y != 0:
            dau_cau = y
            chars[index] = bang_nguyen_am[x][0]
        if not qu_or_gi or index != 1:
            nguyen_am_index.append(index)
    if len(nguyen_am_index) < 2:
        if qu_or_gi:
            if len(chars) == 2:
                x, y = nguyen_am_to_ids.get(chars[1])
                chars[1] = bang_nguyen_am[x][dau_cau]
            else:
                x, y = nguyen_am_to_ids.get(chars[2], (-1, -1))
                if x != -1:
                    chars[2] = bang_nguyen_am[x][dau_cau]
                else:
                    chars[1] = bang_nguyen_am[5][dau_cau] if chars[1] == 'i' else bang_nguyen_am[9][dau_cau]
            return ''.join(chars)
        return word
 
    for index in nguyen_am_index:
        x, y = nguyen_am_to_ids[chars[index]]
        if x == 4 or x == 8:  # ê, ơ
            chars[index] = bang_nguyen_am[x][dau_cau]
            return ''.join(chars)
 
    if len(nguyen_am_index) == 2:
        if nguyen_am_index[-1] == len(chars) - 1:
            x, y = nguyen_am_to_ids[chars[nguyen_am_index[0]]]
            chars[nguyen_am_index[0]] = bang_nguyen_am[x][dau_cau]
        else:
            x, y = nguyen_am_to_ids[chars[nguyen_am_index[1]]]
            chars[nguyen_am_index[1]] = bang_nguyen_am[x][dau_cau]
    else:
        x, y = nguyen_am_to_ids[chars[nguyen_am_index[1]]]
        chars[nguyen_am_index[1]] = bang_nguyen_am[x][dau_cau]
    return ''.join(chars)

def is_valid_vietnam_word(word):
    chars = list(word)
    nguyen_am_index = -1
    for index, char in enumerate(chars):
        x, y = nguyen_am_to_ids.get(char, (-1, -1))
        if x != -1:
            if nguyen_am_index == -1:
                nguyen_am_index = index
            else:
                if index - nguyen_am_index != 1:
                    return False
                nguyen_am_index = index
    return True

def chuan_hoa_dau_cau_tieng_viet(sentence):
    sentence = sentence.lower()
    words = sentence.split()
    for index, word in enumerate(words):
        cw = re.sub(r'(^\p{P}*)([p{L}.]*\p{L}+)(\p{P}*$)', r'\1/\2/\3', word).split('/')
        if len(cw) == 3:
            cw[1] = chuan_hoa_dau_tu_tieng_viet(cw[1])
        words[index] = ''.join(cw)
    return ' '.join(words)

def tach_tu_tieng_viet(text):
    text = ViTokenizer.tokenize(text)
    return text

def chuyen_chu_thuong(text):
    return text.lower()

def chuan_hoa_cau(text):
    text = re.sub(r'[^\s\wáàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệóòỏõọôốồổỗộơớờởỡợíìỉĩịúùủũụưứừửữựýỳỷỹỵđ_]',' ',text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text
    
# def loai_bo_link_va_hastag(text):
#     # Loại bỏ các hashtag
#     text = re.sub(r'#\w+', '', text)
#     # Loại bỏ các liên kết
#     text = re.sub(r'http\S+', '', text)
#     text = re.sub(r'www\S+', '', text)
#     text = re.sub(r'\S+\.\S+', '', text)
#     return text

# def loai_bo_link_va_hastag(text):
#     # Hàm thay thế link chứa "shopee" hoặc "zalo" bằng từ đó
#     def replace_link(match):
#         url = match.group(0)
#         if 'shopee' in url:
#             return 'shopee'
#         elif 'zalo' in url:
#             return 'zalo'
#         else:
#             return ''

#     # Loại bỏ các hashtag, trừ những hashtag có dạng #+ số +k
#     text = re.sub(r'#(?!\d+k\b)\w+', '', text)

#     # Thay thế các liên kết chứa "shopee" hoặc "zalo" bằng từ đó
#     text = re.sub(r'http\S+', replace_link, text)
#     text = re.sub(r'www\S+', replace_link, text)
#     text = re.sub(r'\b\S*\.com\S*\b', replace_link, text)

#     return text
def loai_bo_link_va_hastag(text):
    # Loại bỏ các hashtag
    text = re.sub(r'#\w+', '', text)
    # Loại bỏ các liên kết
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'www\S+', '', text)
    text = re.sub(r'\b\S*\.com\S*\b', '', text)

    # Biểu thức chính quy để phát hiện các số điện thoại (các định dạng phổ biến)
    return text


def loai_bo_emoji(text):
    # Loại bỏ các emoji
    text = re.sub(r'[^\w\s,]', '', text)
    return text

# def loai_bo_khoang_trang_thua(text):
#     # Loại bỏ các khoảng trắng và ký tự đặc biệt thừa
#     text = re.sub(r'[\s\️]+', ' ', text).strip()
#     return text
def loai_bo_khoang_trang_thua(text):
    # Loại bỏ các khoảng trắng, ký tự đặc biệt và các ký tự không mong muốn khác
    text = re.sub(r'[\s\️><...]+', ' ', text).strip()
    return text

def tach_tu_tieng_viet_va_chuan_hoa(text):
    # Tách từ tiếng Việt
    text = ViTokenizer.tokenize(text)
    # Loại bỏ khoảng trắng thừa ngay sau khi tách từ để tránh các khoảng trắng không mong muốn
    text = loai_bo_khoang_trang_thua(text)
    return text
def loai_bo_so_va_ky_tu_k(text):
    # Loại bỏ các số có đuôi 'k'
    text = re.sub(r'\b\d+k\b', '', text)
    return text

def tien_xu_li(text):
    text = loai_bo_link_va_hastag(text)
    text = loai_bo_emoji(text)
    text = chuan_hoa_unicode(text)
    text = chuan_hoa_dau_cau_tieng_viet(text)

    text = tach_tu_tieng_viet_va_chuan_hoa(text)
    text = loai_bo_khoang_trang_thua(text)
#     text = loai_bo_so_va_ky_tu_k(text)  # Thêm bước loại bỏ số có đuôi 'k'

    text = chuyen_chu_thuong(text)
    # text = chuan_hoa_cau(text)
    return text
if __name__ == '__main__':
    
    # print(tien_xu_li("""Công nghệ đột phá về tấm pin mặt trời giúp kiềm chế sự lũng đoạn của Trung quốc

    # Tấm năng lượng mặt trời rất quan trọng đối với quá trình chuyển đổi năng lượng, nhưng hiện tại ngành này đang bị lũng đoạn bởi các sản phẩm giá rẻ từ Trung Quốc. Nhà đầu tư lớn nhất trong ngành sản xuất tấm năng lượng mặt trời của Hoa Kỳ đang áp dụng một công nghệ mới, hy vọng có thể giảm chi phí sản xuất, từ đó giúp xây dựng chuỗi cung ứng ngoài Trung Quốc.

    # Chi tiết xem tại: https://s.shopee.vn/4VHTtezUji"""))
    final_df = pd.read_excel('updated_final_2_spam.xlsx')
    # Thêm cột 'id' với các giá trị ngẫu nhiên
    final_df['id'] = [str(uuid.uuid4()) for _ in range(len(final_df))]

    # Lưu lại file Excel mới
    final_df.to_excel('full_spam_with_id.xlsx', index=False)

