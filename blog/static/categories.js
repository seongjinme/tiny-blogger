import { btn_edit_slug_action, fill_slug, slugify, enable_submit, cancel_submit } from './script.js';

create_category_open_modal.addEventListener('click', add_create_event_listener);
submit_sort_category.addEventListener('click', get_category_order);

const edit_category_btn_list = document.querySelectorAll('.edit_category_open_modal');
const delete_category_btn_list = document.querySelectorAll('.delete_category_open_modal');
const category_lists = document.querySelectorAll('ul#category_list > li');

for (let i = 0; i < category_lists.length; i++) {
    edit_category_btn_list[i].addEventListener('click', add_edit_event_listener);
}

for (let i = 0; i < category_lists.length; i++) {
    delete_category_btn_list[i].addEventListener('click', set_delete_category_contents);
}

function category_global_variables(mode) {
    let values;
    if (mode == 'create') {
        values = {
            'context': 'category',
            'form': create_category,
            'title': create_category_name,
            'slug': create_category_slug,
            'slug_length_max': 32,
            'slug_url': create_category_slug_url,
            'btn_edit_slug': create_category_btn_edit_slug,
            'btn_cancel': create_category_btn_cancel,
            'btn_close': create_category_modal_close,
            'btn_submit': create_category_btn_submit
        };
    } else if (mode == 'edit') {
        values = {
            'context': 'category',
            'form': edit_category,
            'id': edit_category_id,
            'title': edit_category_name,
            'slug': edit_category_slug,
            'slug_length_max': 32,
            'slug_url': edit_category_slug_url,
            'btn_edit_slug': edit_category_btn_edit_slug,
            'btn_cancel': edit_category_btn_cancel,
            'btn_close': edit_category_modal_close,
            'btn_submit': edit_category_btn_submit
        };
    }
    return values;
};

function add_create_event_listener() {
    const g = category_global_variables('create');

    g.form.addEventListener('input', run_create_enable_submit);
    g.title.addEventListener('change', run_create_change_slug_value);
    g.btn_edit_slug.addEventListener('click', run_create_btn_edit_slug_action);
    g.btn_cancel.addEventListener('click', run_create_close_modal);
    g.btn_close.addEventListener('click', run_create_close_modal);
}

function run_create_enable_submit() {
    const g = category_global_variables('create');
    enable_submit(g.title, g.slug, g.context, g.btn_submit);
}

function run_create_change_slug_value() {
    const g = category_global_variables('create');
    change_slug_value(g.context, g.title, g.slug, g.slug_url, g.btn_edit_slug, g.btn_submit);
}

function run_create_btn_edit_slug_action() {
    const g = category_global_variables('create');
    btn_edit_slug_action(g.context, g.title, g.slug, g.slug_url, g.btn_edit_slug, g.slug_length_max, g.btn_submit);
}

function run_create_close_modal() {
    const g = category_global_variables('create');
    cancel_submit(g.title, g.slug, g.slug_url, g.context, g.btn_edit_slug);
    remove_create_event_listener(g);
}

function remove_create_event_listener(g) {
    g.form.removeEventListener('input', run_create_enable_submit);
    g.title.removeEventListener('change', run_create_change_slug_value);
    g.btn_edit_slug.removeEventListener('click', run_create_btn_edit_slug_action);
    g.btn_cancel.removeEventListener('click', run_create_close_modal);
    g.btn_close.removeEventListener('click', run_create_close_modal);
}

function change_slug_value(context, title, slug, slug_url, btn_edit_slug, btn_submit) {
    slug.value = slugify(title.value);
    slug_url.textContent = slug.value;
    btn_edit_slug.disabled = !slug.value;
    enable_submit(title, slug, context, btn_submit);
}

function add_edit_event_listener() {
    const g = category_global_variables('edit');

    g.id.value = this.parentElement.id;
    g.title.value = this.parentElement.querySelector('span.mr-auto.category_name').textContent;
    g.slug.value = this.parentElement.querySelector('span.d-none.category_slug').textContent;
    g.slug_url.textContent = this.parentElement.querySelector('span.d-none.category_slug').textContent;
    g.btn_edit_slug.disabled = !g.slug.value;

    g.form.addEventListener('input', run_edit_enable_submit);
    g.title.addEventListener('change', run_edit_change_slug_value);
    g.btn_edit_slug.addEventListener('click', run_edit_btn_edit_slug_action);
    g.btn_cancel.addEventListener('click', run_edit_close_modal);
    g.btn_close.addEventListener('click', run_edit_close_modal);
}

function run_edit_enable_submit() {
    const g = category_global_variables('edit');
    enable_submit(g.title, g.slug, g.context, g.btn_submit);
}

function run_edit_change_slug_value() {
    const g = category_global_variables('edit');
    change_slug_value(g.context, g.title, g.slug, g.slug_url, g.btn_edit_slug, g.btn_submit);
}

function run_edit_btn_edit_slug_action() {
    const g = category_global_variables('edit');
    btn_edit_slug_action(g.context, g.title, g.slug, g.slug_url, g.btn_edit_slug, g.slug_length_max, g.btn_submit);
}

function run_edit_close_modal() {
    const g = category_global_variables('edit');
    cancel_submit(g.title, g.slug, g.slug_url, g.context, g.btn_edit_slug);
    remove_edit_event_listener(g);
}

function remove_edit_event_listener(g) {
    g.form.removeEventListener('input', run_edit_enable_submit);
    g.title.removeEventListener('change', run_edit_change_slug_value);
    g.btn_edit_slug.removeEventListener('click', run_edit_btn_edit_slug_action);
    g.btn_cancel.removeEventListener('click', run_edit_close_modal);
    g.btn_close.removeEventListener('click', run_edit_close_modal);
}

function set_delete_category_contents() {
    const category_id = this.parentElement.id;
    const category_name = this.parentElement.querySelector('span.mr-auto.category_name').textContent;
    document.getElementById('delete_category_id').value = category_id;
    document.getElementById('delete_category_name').value = category_name;
    document.getElementById('delete_category_name_text').textContent = category_name;
}

function get_category_order() {
    const list = document.getElementById('category_list').getElementsByTagName('li');
    let id_list = [];
    for (let i = 0; i < list.length; i++) {
        id_list.push(list[i].id);
    }
    sort_category_order.value = id_list;
}