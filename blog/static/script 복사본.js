const form = document.querySelector('form');

const title = document.querySelector('#title');
const title_error = document.querySelector('#title + span.error');

const slug = document.querySelector('#slug');
const slug_error = document.querySelector('#slug + span.error');

const body = document.querySelector('#body');

title.addEventListener("input", () => {
    title.classList.add("validated")

    if (title.validity.valid) {
        title_error.textContent = '';
        title_error.className = 'error';
    } else {
        show_error_title();
    }
});

slug.addEventListener("input", () => {
   slug.classList.add("validated")

   if (slug.validity.valid) {
        slug_error.textContent = '';
        slug_error.className = 'error';
    } else {
        show_error_slug();
    }
});

body.addEventListener("input", () => {
   body.classList.add("validated")
});

form.addEventListener("input", () => {
    document.getElementById('submit').disabled = !form.checkValidity()
});

function show_error_title() {
    if (title.validity.tooLong || title.validity.tooShort) {
        title_error.innerHTML = 'Title should be between 1 and 100 characters long.'
    }
}

function show_error_slug() {
    if (slug.validity.tooLong || slug.validity.tooShort) {
        slug_error.innerHTML = 'URL Slug should be between 1 and 100 characters long.'
    } else if (slug.validity.patternMismatch) {
        slug_error.innerHTML = 'URL Slug should be followed by <a href="https://en.wikipedia.org/wiki/Clean_URL#Slug">"Clean URL"</a> rules.'
    }
}