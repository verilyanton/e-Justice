<?php
/*
$fcsv = file("logs/parsed-docs.csv");
$d = [];
foreach ($fcsv as $l) {
  $csv = str_getcsv($l);
  if (!in_array($csv[3], ["md5", "", "1197f290bae092c70a6cf07a223ed8bc"]))
    array_push($d, $csv[1]);
}
foreach (array_unique($d) as $i => $doc_id) {
    echo $doc_id . " "; /*
  $f = fopen("data/lex.justice.md/html/raw/" . $doc_id . ".html", "w");
  $a = file_get_contents("http://lex.justice.md/md/" . $doc_id);
  fwrite($f, $a);
  fclose($f); *
  }
}

*/
// $filename = "logs/last-parsed-mo-no.txt";
// $mo_no = file_get_contents($filename) - 1;
$dir_local = "data/lex.justice.md/mo-html-raw/";
$mo_no = 2017;
if ($mo_no > 0) {
  // file_put_contents($filename, $mo_no);
  $f = fopen($dir_local . $mo_no . ".html", "w");
  $a = file_get_contents("https://www.monitorul.md/monitor/v-" . $mo_no . "-v/");
  fwrite($f, $a);
  fclose($f);
}
