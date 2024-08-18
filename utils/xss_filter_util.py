import bleach

def xss_filter(text):
    # 定义允许的标签和属性
    allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'br', 'em', 'i', 'li',
                    'ol', 'strong', 'ul', 'h1', 'h2', 'p']
    allowed_attributes = {'a': ['href', 'title'], 'abbr': ['title'],
                          'acronym': ['title'], '*': ['class']}
    # 使用bleach清理HTML
    clean_html = bleach.clean(text, tags=allowed_tags, attributes=allowed_attributes)
    return clean_html

if __name__ == '__main__':
    print(xss_filter("<script>alert('XSS')</script><p>This is a safe paragraph.</p>"))