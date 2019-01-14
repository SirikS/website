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
- Doorverwijzen naar profiel aanpas pagina

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
- Controle of gebruiker eigenaar is van profiel
- Zo ja, laad bewerkknop voor profiel die redirect naar profiel beheerpagina.

@beheer ( Beheerpagina voor eigen profiel. (POST en GET))
- Controle voor sessie gebruiker (Gebruiker moet ingelogt zijn)
- Laad velden met aanpasbare gegevens
- Vul velden met huidige data uit database. (Kan ook default waarde zijn.)
Na drukken op 'bijwerken'
- Controle voor correctheid (Velden niet leeg?)
- Aangepaste gegevens in database updaten
- Doorverwijzen naar profielpagina

@volg (Volg of ontvolg profielen op profielpagina. (POST en GET))
- Controle of gebruiker desbetreffende profiel al volgt
- Zo ja, verwijder gebruiker uit volgers database van profiel
- Anders, voeg gebruiker toe aan database volgers profiel

@upload (Pagina om bericht te plaatsen met foto of GIF. (POST en GET))
- Controle voor sessie gebruiker (Gebruiker moet ingelogt zijn)
- FotoID aanmaken (Mocht dit niet in de database kunnen)
- Gegevens toevoegen aan database (ID, fotoID, caption, totaallikes, totaaldislikes, titel)
- Doorverwijzen naar profielpagina

@verwijderen (Bericht verwijderen van eigen profiel. (POST en GET))
- Controle voor sessie gebruiker (Gebruiker moet ingelogt zijn)
- Laad foto's geplaatst door profiel
- Maak foto's selecteerbaar
- Verwijder geselecteerde foto's uit database
- Doorverwijzen naar profielpagina

@fotoweergave

@likedislike

@comment

@share

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
