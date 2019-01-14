# Technisch voorstel

## Controllers

@login (Knop met login dropdown op frontpage.(POST en GET))
- Controle voor correctheid (Velden niet leeg?)
- Controle voor gebruikersnaam en wachtwoord (Is de combinatie correct?)
- Sessie van gebruiker opslaan
- Doorverwijzen naar home gebruiker

@register (Registratieformulier op frontpage. (POST en GET))
- Controle voor correctheid (Velden niet leeg?)
- Controle voor gebruikersnaam (Bestaat deze al?)
- Controle voor wachtwoord en confirmation wachtwoord ( Zijn deze hetzelfde?)
- Controle voor e-mail ( Is er echt een email ingevuld?)
- Gebruiker toevoegen aan database
- Sessie van gebruiker opslaan
- Doorverwijzen naar profiel beheerpagina

@logout (logt gebruiker uit. (POST))
- Sessie van gebruiker verwijderen
- Doorverwijzen naar frontpage

@zoek (Zoek naar andere profielen in zoekbalk rechtsboven. (POST en GET))
- Database doorzoeken op query
- Doorverwijzen naar zoekresultaten pagina
- Controle voor sessie gebruiker (Gebruiker moet ingelogt zijn)
- Zoekresulaten tonen voor query uit data (Op basis van gebruikersnaam worden profielfoto, bio (en volgers) geladen.)

@profiel (Profielpagina. (POST en GET))
- Controle voor sessie gebruiker (Gebruiker moet ingelogt zijn)
- Laad profielfoto
- Laad bio
- Laad aantal volgers
- Laad foto's geplaatst door profiel
- Laad gelikte foto's door profiel
- Laad likes en dislikes op 
- Controle of gebruiker eigenaar is van profiel
- Zo ja, laad bewerkknop voor profiel die redirect naar profiel beheerpagina.

@beheer ( Beheerpagina voor eigen profiel. (POST en GET))
- Controle voor sessie gebruiker (Gebruiker moet ingelogt zijn)
- Laad velden met aanpasbare gegevens
- Vul velden met huidige data uit database. (Kan ook default waarde zijn.)
Na drukken op 'bijwerken'
- Controle voor correctheid (Velden niet leeg?, maximaal aantal karakters niet overschreden)
- Aangepaste gegevens in database updaten
- Doorverwijzen naar profielpagina

@volg (Volg of ontvolg profielen op profielpagina. (POST en GET))
- Controle of gebruiker desbetreffende profiel al volgt
- Zo ja, verwijder gebruiker uit volgers database van profiel
- Anders, voeg gebruiker toe aan database volgers profiel

@upload (Pagina om bericht te plaatsen met foto of GIF. (POST en GET))
- Controle voor sessie gebruiker (Gebruiker moet ingelogt zijn)
- Controle voor correctheid (Is het maximaal aantal karakters niet overschreden.)
- FotoID aanmaken (Mocht dit niet in de database kunnen)
- Gegevens toevoegen aan database (ID, fotoID, caption, totaallikes, totaaldislikes, titel)
- Doorverwijzen naar profielpagina

@verwijderen (Bericht verwijderen van eigen profiel. (POST en GET))
- Controle voor sessie gebruiker (Gebruiker moet ingelogt zijn)
- Laad foto's geplaatst door profiel
- Maak foto's selecteerbaar
- Verwijder geselecteerde foto's uit database
- Doorverwijzen naar profielpagina

@home (Home scherm van gebruiker (POST en GET))
- Controle voor sessie gebruiker (Gebruiker moet ingelogt zijn)
- Laad random fotoID
- Controle of gebruiker bericht al eens heeft beoordeeld (Loop door random fotoID's tot foto wordt gevonden, die nog niet is beoordeeld  door gebruiker.)
- Laad foto met bijbehorende caption, comments, profielfoto van plaatser, profielnaam van plaatser, titel, timestamp.
- Laad like en dislike knop 
- Laad share mogelijkheden

@like (Like bericht. (POST en GET))
- Controle of gebruiker bericht al heeft beoordeeld
- Voeg bericht toe aan database van gelikte foto's van gebruiker
- Update aantal likes op bericht (+1)
- Laad volgende foto uit correcte foto lijst

@dislike (Dislike bericht. (POST en GET))
- Controle of gebruiker bericht al heeft beoordeeld
- Voeg bericht toe aan database van gedislikte foto's van gebruiker
- Update aantal dislikes op bericht (+1)
- Laad volgende foto uit correcte foto lijst

@comment (Laat een reactie achter op een bericht. (POST en GET))
- Controle op correctheid (Maximaal aantal karakters.)
- Voeg comment toe aan database met ID
- Refresh comments (met script?)

@share (Mogelijkheid tot delen van bericht. (POST en GET))
- Voeg data toe aan parameters van deelopties (Zoals link, foto en caption)
- Open gekozen deeloptie in nieuw tabblad

## Views

## Models/helpers
- <strong>Apology: </strong><em>A basic apology for us to see what is going wrong.</em>
- <strong>Register: </strong><em>A way to insert a account into the database.</em>
- <strong>Login: </strong><em>A way to check if username and password are correct.</em>
- <strong>Login required: </strong><em>A funcition to use to make sure the user is signed in, else it cant see the pages.</em>
- <strong>Upload: </strong><em>A function that uploads the picture to a database, with all fields.</em>
- <strong>Like: </strong><em>Inserts a line into a database containing two value's, a picture id and userid.</em>
- <strong>Follow: </strong><em>Inserts a line into a database containing two value's which is two userid's.</em>
 </ul>

## Plugins en frameworks
