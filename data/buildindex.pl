#!/usr/bin/perl -W


# receive UnicodeData.txt

my (%index);

while ($line = <STDIN>) {
	my (@fields) = split /;/, $line;

	$char_name = $fields[1];
	my @char_words = split / /, $char_name;
	$code = $fields[0];

	foreach $word (@char_words) {
		$index{$word} = "" unless defined $index{$word};
		$index{$word} = $index{$word} . " " . $code;
	}
}

foreach $key (sort keys %index) {
	my (@chars) = split /\s/, $index{$key};

	foreach $char (@chars) {
		if ($char eq "") { next; }
		print "INSERT INTO character_word (character, word) VALUES ('$char', '$key');\n"
	}
}


