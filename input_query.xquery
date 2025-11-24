xquery version "3.1";
declare default element namespace "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15";

(:let $collection := uri-collection('export_job_19138314?select=*.xml;recurse=yes')
let $docs :=
        for $uri in $collection
        return doc($uri)
let $contents := $docs//PcGts
for $page in $contents
where $page[//*[contains(@custom, 'type:multiplication')]]
return <result>{$page/base-uri()}</result>:)

(:how many images do the classes appear in?:)
let $collection := uri-collection('export_job_19138314?select=*.xml;recurse=yes')
let $docs :=
        for $uri in $collection
        return doc($uri)
let $contents := $docs//PcGts
let $regions := $contents//*[contains(./name(), 'Region') and Coords]
let $custom := $regions/@custom

let $annotation-types :=
    let $types := 
        for $instance in $custom
        return substring-before(substring-after($instance, '{type:'), ';}')
    return distinct-values($types)

for $type in $annotation-types
where $type != ''
let $count := count($contents[//*[contains(@custom, $type)]])
order by $count descending
return <count type="{$type}">{$count}</count>

(:how many regions are there, and how many of them have classes?:)
(:let $collection := uri-collection('export_job_19138314?select=*.xml;recurse=yes')
let $docs :=
        for $uri in $collection
        return doc($uri)
let $contents := $docs//PcGts
let $regions := $contents//*[contains(./name(), 'Region') and Coords]
let $regions-with-classes := $regions[contains(@custom/data(), '{type:')]
return (count($regions), count($regions-with-classes)):)

(:what regions do classes appear in?:)
(:let $collection := uri-collection('export_job_19138314?select=*.xml;recurse=yes')
let $docs :=
        for $uri in $collection
        return doc($uri)
let $contents := $docs//PcGts
let $regions := $contents//*[contains(./name(), 'Region') and Coords]
for $mulregion in distinct-values($regions[contains(@custom/data(), 'multiplication_table')]/name())
return ($mulregion, count($regions[name() = $mulregion and contains(@custom/data(), 'multiplication_table')])):)


(:what classes exist in all regions and how often does each appear?:)
(:let $collection := uri-collection('export_job_19138314?select=*.xml;recurse=yes')
let $docs :=
        for $uri in $collection
        return doc($uri)
let $contents := $docs//PcGts
let $regions := $contents//*[contains(./name(), 'Region') and Coords]
let $custom := $regions/@custom

let $annotation-types :=
    let $types := 
        for $instance in $custom
        return substring-before(substring-after($instance, '{type:'), ';}')
    return distinct-values($types)

for $type in $annotation-types
where $type != ''
let $count := count($custom[contains(., $type)])
order by $count descending
return <count type="{$type}">{$count}</count>:)
