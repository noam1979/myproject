-- all rows
SELECT * FROM myapp_book;
-- filter: specific author
SELECT * FROM myapp_book
WHERE author = 'William';
-- partial match (case-insensitive in SQLite by default)
-- SELECT * FROM myapp_book
-- WHERE title LIKE '%django%';
-- order and limit
-- SELECT * FROM myapp_book
-- ORDER BY published_year DESC
-- LIMIT 5;
--a few aggregates
-- SELECT COUNT(*) AS total_books FROM myapp_book;
-- SELECT AVG(pages) AS avg_pages FROM myapp_book;
-- SELECT MAX(published_year) AS newest FROM myapp_book
