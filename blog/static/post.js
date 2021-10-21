import { btn_edit_slug_action, fill_slug, slugify, enable_submit } from './script.js';

const context = 'post';
const form = create;
const slug_length_max = 200;
const btn_cancel = null;
const btn_submit = submit;

btn_edit_slug.disabled = !slug.value;

form.addEventListener('input', event => enable_submit(title, slug, context, btn_submit));

title.addEventListener('change', () => {
    slug.value = slugify(title.value);
    slug_url.textContent = slug.value;
    btn_edit_slug.disabled = !slug.value;
    enable_submit(title, slug, context, btn_submit);
});

btn_edit_slug.addEventListener('click', event => btn_edit_slug_action(context, title, slug, slug_url, btn_edit_slug, slug_length_max, btn_submit));