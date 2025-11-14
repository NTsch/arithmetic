xquery version "3.1";
declare default element namespace "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15";

let $collection := uri-collection('export_job_19138314?select=*.xml;recurse=yes')
let $docs :=
        for $uri in $collection
        return doc($uri)
let $contents := $docs//PcGts
let $math := $contents//MathsRegion
let $custom := $math/@custom

let $annotation-types :=
    let $types := 
        for $instance in $custom
        return substring-before(substring-after($instance, '{type:'), ';}')
    return distinct-values($types)

for $type in $annotation-types
where $type != ''
let $count := count($custom[contains(., $type)])
order by $count descending
return <count type="{$type}">{$count}</count>
