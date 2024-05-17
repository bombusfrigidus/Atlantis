------------
Introduction
------------

This file duplicates basic information from README.md. Render README.md or see github.com/bombusfrigidus/Atlantis for more information.

Atlantis is a CK3 TC template by BOMBUS_FRIGIDUS (github.com/bombusfrigidus, bombus_frigidus@gmail.com, bombus_frigidus on Discord).

Atlantis is compatible with CK3 1.12.5 as of 2024/05/16.

---------------------------
What does this template do?
---------------------------

Atlantis replaces or otherwise masks all provinces, titles, regions, cultures, religions, and characters in CK3 and provides a toy TC.

Where earlier templates deleted all vanilla titles, cultures, and religions, this template preserves them through a few steps:
 - All duchies, kingdoms, and empires are preserved as landless titles with a shared placeholder capital.
 - All cultures and religions are left untouched; all holy sites are set to a shared placeholder county.

Like earlier templates, Atlantis eliminates all vanilla provinces and counties and related references, with some references filled in with placeholders.

Atlantis also eliminates all vanilla characters and related references, with some references filled in with a placeholder.

The placeholder province is 1, b_atlantis. The placeholder county is 1, c_atlantis. The placeholder character is 1, "Atlas."

Atlantis also modifies files so that there are no errors logged through game start and minimal errors logged afterward.

The upsides of this approach are:
 - Easier TC development with fewer errors to resolve from scratch.
 - Easier TC maintenance with fewer modified files that can conflict with patches.
 - Easier restoration of vanilla content, for example in a historical total conversion featuring vanilla religions.

The downsides of this approach are:
 - This template is more opinionated than earlier templates, in that Atlantis contains more than the bare minimum to start the game.
 - A more fragile and less intuitive template, in that preserving titles, cultures, and religions risks unexpected errors later in development.

So, take it or leave it. 

--------------------------------------------
What am I supposed to do with this template?
--------------------------------------------

You're reading this because you want to develop a total conversion for CK3. First of all, don't, unless you have thousands of hours to spare and experience with smaller mods.

Second of all, before you can develop your fantastical or historical world in CK3, you'll need to get the world of CK3 out of the way. This template does that.

The next steps are all about replacing the template's placeholders -- all the "Atlantis" stuff -- with the first pieces of your own mod.
 - [finish this with the tutorial]
 - map_data
 - common/landed_titles
 - common/province_terrain
 - history
 - localization
 - bonus

[preview of next stuff, direct to wiki, forum, CK3 Discord, Co-op]

