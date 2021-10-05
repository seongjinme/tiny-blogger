import bleach


def sanitize_html(html):
    allowed_tags = ['a', 'abbr', 'acronym', 'address', 'b', 'br', 'code', 'div', 'dl', 'dt',
                    'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img', 'iframe'
                    'li', 'ol', 'p', 'pre', 'q', 's', 'small', 'strike', 'strong',
                    'span', 'sub', 'sup', 'table', 'tbody', 'td', 'tfoot', 'th',
                    'thead', 'tr', 'tt', 'u', 'ul', 'video']

    allowed_attributes = {
        '*': ['style'],
        'a': ['href', 'title', 'target'],
        'img': ['src', 'width', 'height', 'alt'],
        'iframe': ['src', 'width', 'height', 'title', 'frameborder', 'allow', 'allowfullscreen'],
        'video': ['controls', 'width', 'height', 'allowfullscreen', 'preload', 'poster']
    }

    allowed_styles = ['color', 'background-color', 'font', 'font-weight',
                      'width', 'height', 'text-decoration', 'text-align']

    allowed_protocols = ['http', 'https', 'mailto', 'data']

    return bleach.clean(html,
                        tags=allowed_tags,
                        attributes=allowed_attributes,
                        styles=allowed_styles,
                        protocols=allowed_protocols,
                        strip=True)
