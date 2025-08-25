# reading

<div id="book-list"></div>
<script>

    function extractReadDate(extra) {
        if (!extra) return '';
        const match = extra.match(/read:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})/);
        return match ? match[1] : '';
    }

    async function fetchBooks() {
        const collectionKey = '9PEVG7Y5';
        const userID = '7402845';
        const zoteroUrl = `https://api.zotero.org/users/${userID}/collections/${collectionKey}/items?limit=100`;

        const bookList = document.getElementById('book-list');

        try {
            const res = await fetch(zoteroUrl, {
                headers: { 'Accept': 'application/json' }
            });
            const items = await res.json();
            if (!items.length) {
                bookList.innerHTML = "<p>No items found in your Zotero library.</p>";
                return;
            }

            const books = [];
            const notesByParent = {};

            for (const item of items) {
                if (item.data.itemType === 'note') {
                    const parent = item.data.parentItem;
                    if (!notesByParent[parent]) notesByParent[parent] = [];
                    notesByParent[parent].push(item.data.note);
                }
            }

            for (const item of items) {
                if (item.data.itemType !== 'book') continue;

                const data = item.data;
                const isbn = data.ISBN || 'N/A';

                let authors = '';
                if (Array.isArray(data.creators)) {
                    const filtered = data.creators.filter(c => c.creatorType === "author");
                    authors = filtered.map(a => [a.firstName, a.lastName].filter(Boolean).join(' ')).join(', ');
                }

                const title = data.title || `[No title — ISBN: ${isbn}]`;
                const readDate = extractReadDate(data.extra);
                const timestamp = readDate ? Date.parse(readDate) : 0;
                const notes = notesByParent[data.key] || [];

                books.push({
                    readDate,
                    title,
                    authors: authors || `[Unknown author — ISBN: ${isbn}]`,
                    timestamp,
                    notes
                });
            }

            books.sort((a, b) => b.timestamp - a.timestamp);

            bookList.innerHTML = books.map(book =>
                `<div>
                    <p>${book.readDate} <strong>${book.title}</strong> (${book.authors})</p>
                    ${book.notes.map(note => `<div>${note}</div>`).join('')}
                </div>`
            ).join('');

        } catch (err) {
            bookList.innerHTML = "<p>Error fetching books.</p>";
            console.error(err);
        }
    }
    fetchBooks();
</script>
