# iBus Unicode DB

[Video demo](https://www.youtube.com/watch?v=4VavXqD-nXs)

This is an input method that lets you search the Unicode database as you type. Something like using the character map while typing, except easier. For example, you can type the search terms "greek alpha", and it will offer you the Unicode characters corresponding to "Greek capital letter alpha with tonos", "Greek capital letter alpha", "Greek small letter alpha" etc.

This input method also shows you the unicode sequence of the characters that you type. If you ever find it easier to just memorize a frequently used character than to search for it, you can do that too!

Finally, this input method is probably most useful if integrated into other input methods / keyboards.
For example, iBus currently lets users enter arbitrary unicode characters when users type `Ctrl+Shift+U <unicode sequence>.`
However, this only works as well as you can remember the unicode sequences. And character maps can be a pain, especially if you start to use a lot of Greek letters in your documents.

Arguably you can use TeX, but in all honesty you cannot use TeX everywhere (e.g. in Google Chrome, in GEdit), so this method is better.

Search sequences are activated by Ctrl+Shift+U, followed by the apostrophe (').

## Installation

### Step 1
    $ git clone https://github.com/xkjyeah/ibus-unicode-db.git

### Step 2
    $ cd ibus-unicode-db
    $ ./autogen.sh && make && sudo make install

### Step 3

If you are using Ubuntu 13.10 or later

    $ gnome-control-center region

If you are using Ubuntu 12.10 or earlier...

    $ ibus-setup

Then, add the "English (UnicodeDb)" input method

(If you are using Ubuntu 13.04, or any other distributions, try both methods anyway)

## Future work

### Unihan database
I have not included the Unihan database, but it could/should/would be helpful for non-Chinese/Japanese/Korean people looking for their favourite Chinese character.

### Windows port
A Windows port is underway at https://github.com/xkjyeah/itf-unicode-db.

23 Dec 2014
