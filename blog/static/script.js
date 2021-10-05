function search_post() {
    text = q.value;

    // Remove '--' characters and duplicated whitespaces
    text = text.replace(/(--)/g, '')
        .replace(/(\s)\1+/g, ' ');

    // Remove whitespace at the beginning or end
    text = q.value.trim();

    return text;
}