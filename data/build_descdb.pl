#!/usr/bin/perl -W


# receive UnicodeData.txt

my (%index);

while ($line = <STDIN>) {
	my (@fields) = split /;/, $line;

	$char_name = $fields[1];
	my @char_words = split / /, $char_name;
	$code = $fields[0];

	print "INSERT INTO character_desc (character, desc) VALUES ('$code', '$char_name');\n";


	foreach $word (@char_words) {
		$index{$word} = "" unless defined $index{$word};
		$index{$word} = $index{$word} . " " . $code;
	}
}

