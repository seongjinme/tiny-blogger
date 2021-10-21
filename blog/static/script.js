export function btn_edit_slug_action(context, title, slug, slug_url, btn_edit_slug, slug_length_max, btn_submit) {
    if (slug.readOnly) {
        slug.readOnly = false;
        btn_edit_slug.textContent = 'Done';
        btn_edit_slug.className = 'btn btn-success';
    } else {
        slug.readOnly = true;
        btn_edit_slug.textContent = 'Edit';
        btn_edit_slug.className = 'btn btn-primary';
        fill_slug(slug, title, slug_length_max);
        slug_url.textContent = slug.value;
    }
    enable_submit(title, slug, context, btn_submit);
}

export function fill_slug(slug, title, slug_length_max) {
    slug.value = slugify(slug.value);
    if (!slug.value) {
        slug.value = slugify(title.value, slug_length_max);
    }
}

export function slugify(text, slug_length_max) {
    // This codes are applied version of the character conversion script in Ghost CMS, made by Ghost Foundation Ltd.
    // https://github.com/TryGhost/Ghost

    // Remove whitespace at the beginning or end
    text = text.trim();

    // Remove URL reserved chars: `@:/?#[]!$&()*+,;=` as well as `\%<>|^~£"{}` and \`
    text = text.replace(/(\.|@|:|\/|\?|#|\[|\]|!|\$|&|\(|\)|\*|\+|,|;|=|\\|%|<|>|\||\^|~|"|\{|\}|`|–|—)/g, '')
        // Remove apostrophes
        .replace(/'/g, '')
        // Replace whitespaces and '_' to '-'
        .replace(/(\s)|(_)/g, '-')
        // Remove broken Korean letters
        .replace(/[ㄱ-ㅎㅏ-ㅣ]/g, '')
        // Remove duplicated '-'
        .replace(/(-)\1+/g, '-')
        // Remove '-' at the beginning or end
        .replace(/^[-]|[-]$/g, '')
        // Make the whole thing lowercase
        .toLowerCase();

    // Check and trim whitespace at the beginning or end again
    text = text.trim();

    // Limit length of URL slug to 200 characters
    text = text.substr(0, slug_length_max);

    return text;
}

export function enable_submit(title, slug, context, btn_submit) {
    if (context == 'category') {
        btn_submit.disabled = !(title.value && slug.readOnly && slug.value);
    }
    else if (context == 'post') {
        let content = document.querySelector('div.note-editable.card-block');
        btn_submit.disabled = !(title.value && slug.readOnly && slug.value && category.options[category.selectedIndex].value && (content.innerHTML != '<p><br></p>' && content.innerHTML != ''));
    }
}

export function cancel_submit(title, slug, slug_url, context, btn_edit_slug) {
    if (context == 'category') {
        title.value = '';
        slug.value = '';
        slug_url.textContent = '';
        btn_edit_slug.textContent = 'Edit';
        btn_edit_slug.className = 'btn btn-primary';
        btn_edit_slug.disabled = true;
        slug.readOnly = true;
    }
}