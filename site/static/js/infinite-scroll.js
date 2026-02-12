(function () {
    var pageFooter = document.querySelector('footer.page-footer');
    if (!pageFooter) return; // no pagination on this page

    var nextAnchor = pageFooter.querySelector('.pagination .next');
    if (!nextAnchor) return; // already on the last page

    // Hide the static pagination controls
    pageFooter.style.display = 'none';

    // Sentinel element — sits below the last article; triggers load when visible
    var sentinel = document.createElement('div');
    sentinel.id = 'infinite-scroll-sentinel';
    pageFooter.parentNode.insertBefore(sentinel, pageFooter);

    // Spinner shown while fetching
    var spinner = document.createElement('p');
    spinner.id = 'infinite-scroll-spinner';
    spinner.textContent = 'Loading…';
    spinner.style.cssText = 'text-align:center;padding:1.5rem 0;display:none;color:var(--secondary)';
    pageFooter.parentNode.insertBefore(spinner, pageFooter);

    var nextUrl = nextAnchor.href;
    var loading  = false;

    function loadNext() {
        if (loading || !nextUrl) return;
        loading = true;
        spinner.style.display = 'block';

        fetch(nextUrl)
            .then(function (res) { return res.text(); })
            .then(function (html) {
                var doc = new DOMParser().parseFromString(html, 'text/html');

                // Grab all post articles from the fetched page
                var articles = doc.querySelectorAll('article.post-entry, article.first-entry');
                articles.forEach(function (a) {
                    sentinel.parentNode.insertBefore(a, sentinel);
                });

                // Advance to next page URL (or stop if none)
                var newNext = doc.querySelector('footer.page-footer .pagination .next');
                nextUrl = newNext ? newNext.href : null;
            })
            .catch(function (err) {
                console.warn('Infinite scroll fetch failed:', err);
                nextUrl = null;
            })
            .finally(function () {
                loading = false;
                spinner.style.display = 'none';
                if (!nextUrl) {
                    spinner.style.display = 'none';
                    observer.disconnect();
                }
            });
    }

    var observer = new IntersectionObserver(function (entries) {
        if (entries[0].isIntersecting) loadNext();
    }, { rootMargin: '300px' });

    observer.observe(sentinel);
})();
