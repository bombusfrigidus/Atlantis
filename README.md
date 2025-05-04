# Introduction

Atlantis is a CK3 TC template. Contact:
 - github.com/bombusfrigidus
 - bombus_frigidus@gmail.com
 - bombus_frigidus on Discord

Atlantis is compatible with CK3 1.16.0.1 as of 2025/05/03. 

The update from 1.15.0.2 is wholly by Striped Honey (stripedhoney on Discord, BiggDeer on GitHub). Cheers!

For more resources on mods, refer to:
 - Crusader Kings III - User Mods | Paradox Interactive Forums
    - https://forum.paradoxplaza.com/forum/forums/crusader-kings-iii-user-mods.1080/
 - Modding - CK3 Wiki - Paradox Wikis
    - https://ck3.paradoxwikis.com/Modding
 - Official Paradox Discord Server for Crusader Kings
    - https://discord.com/invite/ck3
 - CK3 Mod Co-op Discord Server
    - https://discord.com/invite/F7Ta5R2rFR

# What does this template do?

Atlantis replaces or otherwise masks all provinces, titles, regions, cultures, religions, and characters in CK3.

Where previous templates deleted all vanilla titles, cultures, and religions, this template preserves them:
 - All duchies, kingdoms, and empires are preserved as landless titles with a shared placeholder capital.
 - All cultures and religions are left untouched but hidden through GUI changes. 
    - All holy sites are set to a shared placeholder county.

Like previous templates, Atlantis eliminates all vanilla provinces and counties. To address scripted references to vanilla provinces and counties, Atlantis replaces those references with placeholders except in cases where eliminating references is simpler. To address scripted references to vanilla characters, Atlantis replaces those references with a placeholder except in cases where eliminating references is simpler. The placeholder province is 1, corresponding to b_atlantis. The placeholder county is c_atlantis. The placeholder character is 1, "Atlas."

All these deletions and replacements add up to a total conversion that throws no errors through game start.

The upsides of this approach are:
 - Easier TC development with fewer errors to resolve from scratch.
 - Easier TC maintenance with fewer modified files that can conflict with patches.
 - Easier restoration of vanilla content, for example in a historical total conversion featuring vanilla religions.

The downsides of this approach are:
 - This template is more opinionated than previous templates.
 - This template is more fragile and less intuitive than previous templates.

It's worth mentioning that Atlantis replaces whole files, not objects within files. That's inefficient but simpler up front.

# What am I supposed to do with this template?

You're reading this because you want to develop a total conversion for CK3. First, don't, unless you have experience with smaller mods and thousands of hours to spare. Second, even then, don't! Total conversions are difficult, frustrating, and often less than rewarding.

Third, even if you're down with all that, the rest of this document assumes you are familiar with the following:
 - Structure of CK3 files
 - Structure of CK3 mod files
 - Some useful IDE, for example VSC
 - Some useful image editor, for example GIMP
 - Some useful Git interface, for example GitHub and GitHub Desktop

If you are unfamiliar with one of those things, go develop smaller mods to pick up relevant skills.

Fourth, the first step to a total conversion mod is clearing the world of CK3 out of CK3. This template does that.

With this template, you are only some tens of steps from the first step in developing a total conversion. 

Without this template, you are hundreds of steps from the first step in developing a total conversion. 

So, take it or leave it. 

The remainder of this document is a sparse guide to repurposing Atlantis for your project.

# Preliminaries

There are two approaches to developing a total conversion with this template. You can:
 - Change files in Atlantis to build your mod from inside the template
 - Create files in a separate mod to build your mod on top of the template

The first is more intuitive, but the second simplifies compatches. This guide follows the first approach.

So, let's suppose your project is called Lemuria (an analogue to the Atlantis myth) and get into it.

 - Clone Atlantis to your machine, in particular to Paradox Interactive/Crusader Kings III/mod. 
 - Change the folder name from "Atlantis" to "Lemuria" and rename your Git repo while you're at it.
 - Move Atlantis.mod from to Paradox Interactive/Crusader Kings III/mod.
 - Rename Atlantis.mod to Lemuria.mod. 
 - In Lemuria.mod, change the two occurrences of "Atlantis" to "Lemuria," and correct the path.
 - All subsequent file paths are relative to Paradox Interactive/Crusader Kings III/mod/Lemuria.
 - In descriptor.mod, change the single occurrence of "Atlantis" to "Lemuria."
 - In Steam, open launch options for CK3 and add -debug_mode and -develop. 
 - Run the CK3 launcher. Add a playset. Add Lemuria to the playset. 
 - Run CK3 through game start. 
 - If the game crashes or if errors appear in error.log, revisit the previous steps until the problem is resolved.
    - "Revisit the previous steps" applies throughout this guide. If some steps are incorrect, good luck!
 - Close CK3. If you're working in VSC, create a workspace for Lemuria.

# map_data

 - Add your heightmap files and your rivers.png to map_data. Creating those files is outside the scope of this guide.
 - Add your provinces.png to map_data, replacing the provinces.png from Atlantis. 
    - Subsequent steps might be easier if you combine province maps instead.
 - Add your provinces to definitions.csv. 
    - Overwrite the provinces from Atlantis if you've replaced provinces.png instead of combining.
 - Run CK3 through game start. 
    - error.log should have a lot of errors involving your provinces, but none should cause crashes.

# common and map_data

 - Add your provinces to common/landed_titles/00_landed_titles.txt. 
    - Overwrite the titles from Atlantis if you've replaced provinces.png instead of combining.
 - Add your provinces to both files in common/province_terrain. 
    - It's easiest to just duplicate filler entries from Atlantis for now.
 - Add your titles to map_data/geographical_regions/geographical_region.txt. 
    - It's easiest to just replace d_atlantis with your duchy or duchies for now.
 - Add your titles to map_data/island_region if some are islands. This doesn't seem to matter much.
 - Add your provinces to map_data/default.map. Check for discrepancies involving provinces from Atlantis.
 - Run CK3 through game start. 
    - error.log should still have a lot of errors, but different ones, and none should cause crashes.

# common and history

For each of these steps, see Atlantis files for trivial examples. 

 - In common/culture, add one heritage and culture. 
 - In common/religion, add one religion and faith. 
 - In common/dynasties, add one dynasty. 
 - In history/characters, add one character of your culture, faith, and dynasty, with a birth date of 1.1.1.
 - In history/titles, assign your titles to that character on 1.1.1.
 - In history/provinces, assign culture and religion to your provinces. Add holdings if that floats your boat.
 - Run CK3 through game start. error.log should have fewer errors than before. 

# common/bookmarks

 - In common/bookmarks, add a bookmark. Follow Atlantis files for a simple implementation.
 - Go back to history/characters and history/titles to update your character's birth date and date of accession.
 - There are a lot of steps to make a bookmark look done. Those are all fluff and outside the scope of this guide.
 - Run CK3 through game start. 
    - Clean up any bookmark-related crashes or substantial errors before proceeding.

# Housekeeping

If you replaced Atlantis provinces, etc., instead of adding to them, use your IDE to search and replace several terms:

 - Search for b_atlantis. Replace b_atlantis with one of your baronies.
 - Search for c_atlantis. Replace c_atlantis with one of your counties.
 - If you'd like placeholder references to point to a province, character, or dynasty besides "1", replace those.
 - Run CK3 through game start. 
    - Use error.log to check for errors related to replacement of b_atlantis, c_atlantis, etc.

# Next Steps

Of course there's a lot more to do. Your bookmark could look nicer. Your content needs to be localized. It goes on.

But that's beyond this guide. If things have worked up to this point, you have a total conversion running.

If you opted to combine your provinces, etc. with Atlantis instead of replacing Atlantis, go back and replace Atlantis.

Good luck with your mod!
