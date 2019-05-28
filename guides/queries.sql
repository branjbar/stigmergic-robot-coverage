
-- Query to group the matches based on roles and docuemnt types
SELECT 
    score,
    type1,
    type2,
    avg(substring(docu2.date, 7, 12) - substring(docu1.date, 7, 12)) as age, count(*)
FROM
    (SELECT 
        *
    FROM
        links_based.miss_matches
    WHERE
        score = 2
    group by doc1 , doc2) AS T1
        inner join
    all_documents_2014 as docu1
        inner join
    all_documents_2014 as docu2
where
    docu2.id = doc2 and docu1.id = doc1
group by type1 , type2
order by count(*) desc;

-- 
-- select 
--     type1, type2, count(*)
-- FROM
--     (SELECT 
--         *
--     FROM
--         miss_matches
--     where
--         score = 2) as T
-- group by type1 , type2
-- order by count(*) desc;
-- 
-- select 
--     type1, type2, count(*)
-- FROM
--     (SELECT 
--         *
--     FROM
--         miss_matches
--     where
--         score = 2) as T
-- group by type1 , type2
-- order by count(*) desc;


-- find duplicates (death)
select 
    count(*)
from
    (SELECT 
        *
    FROM
        links_based.deceased
    group by `deceased`.`last name` , `deceased`.`first names` , `deceased`.`date of death` , `deceased`.`last name father` , `deceased`.`first names father` , `deceased`.`last name mother` , `deceased`.`first names mother` , `deceased`.`last name partner` , `deceased`.`first names partner`
    having count(*) > 1) as T
    
-- find duplicates (birth)
SELECT 
    count(*)
from
    (select 
        *
    from
        birth
    group by `birth`.`last name` , `birth`.`first names` , `birth`.`date` , `birth`.`last name father` , `birth`.`first names father` , `birth`.`last name mother` , `birth`.`first names mother`
    having count(*) > 1) as T
    
-- find duplicates (marriage)
SELECT 
    count(*)
from
    (select 
        *
    from
        marriage
    group by `marriage`.`date` , `marriage`.`last name groom` , `marriage`.`first names groom` , `marriage`.`last name bride` , `marriage`.`first names bride` , `marriage`.`last name father groom` , `marriage`.`first names father groom` , `marriage`.`last name mother groom` , `marriage`.`first names mother groom` , `marriage`.`last name father bride` , `marriage`.`first names father bride` , `marriage`.`last name mother bride` , `marriage`.`first names mother bride`
    having count(*) > 1) as T
