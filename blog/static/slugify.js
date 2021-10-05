create.addEventListener('input', enable_submit);

title.addEventListener('change', () => {
    slug.value = slugify(title.value);
    update_post_url();
    btn_edit_slug.disabled = !slug.value;
    enable_submit();
});

slug.addEventListener('change', update_post_url)
btn_edit_slug.addEventListener('click', btn_edit_slug_action);

function update_post_url() {
    document.getElementById('post_slug').textContent = slug.value + '/';
}

function btn_edit_slug_action() {
    if (slug.readOnly) {
        btn_edit_slug.textContent = 'Done';
        btn_edit_slug.className = 'btn btn-success';
        slug.readOnly = false;
    } else {
        btn_edit_slug.textContent = 'Edit';
        btn_edit_slug.className = 'btn btn-primary';
        slug.readOnly = true;
        fill_slug();
    }
    enable_submit();
}

function fill_slug() {
    slug.value = slugify(slug.value);
    if (!slug.value) {
        slug.value = slugify(title.value);
    }
    update_post_url();
}

function slugify(text) {
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
    text = text.substr(0, 200)

    return text;
}

function enable_submit() {
    content = document.querySelector('div.note-editable.card-block');
    submit.disabled = !(title.value && slug.readOnly && slug.value && (content.innerHTML != '<p><br></p>' && content.innerHTML != ''));
}