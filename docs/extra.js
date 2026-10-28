/* Dati aggiuntivi (trame, cast, generi) per i film nuovi.
   Questo file NON viene toccato dall'aggiornamento automatico: si possono aggiungere
   qui altri film. Il titolo deve essere uguale a quello mostrato nella pagina. */
var EXTRA = {
  GEN: {
    "Matrix": "Fantascienza · Azione",
    "Resident Evil": "Horror",
    "Carla Lonzi - Dentro e fuori dal mondo": "Documentario",
    "Strange Journey: The Story of Rocky Horror": "Documentario",
    "The Bibi Files": "Documentario",
    "Tomorrow X Together world tour Act: tomorrow": "Film-concerto",
    "Dracula di Bram Stoker 4K": "Horror · Drammatico",
    "Enhypen World Tour Blood Saga": "Film-concerto",
    "Un tranquillo funerale di famiglia": "Commedia",
    "Maigret, l'amore e la morte": "Giallo",
    "Prima della rivoluzione": "Drammatico",
    "La bambola": "Commedia",
    "Il dottor Stranamore, ovvero: come imparai a non preoccuparmi e ad amare la bomba": "Commedia · Satira",
    "Per silenzio e vento": "Documentario",
    "Era meglio domani": "Commedia",
    "Paw Patrol - Missione Dinosauri": "Animazione",
    "Coco": "Animazione",
    "Michael": "Biografico · Musicale",
    "Bts World Tour Arirang in Busan - Live Viewing": "Film-concerto"
  },
  PLOT: {
    "Matrix": "Thomas Anderson, programmatore di giorno e hacker di notte con il nome di Neo, scopre che la realtà che conosce è una simulazione creata dalle macchine. Reclutato da Morpheus e Trinity, si unisce alla resistenza degli umani. Capolavoro fantascientifico delle sorelle Wachowski, tornato in sala.",
    "Resident Evil": "Bryan, un corriere medico, deve consegnare un pacco al remoto ospedale di Raccoon City in una notte invernale di neve. Si ritrova coinvolto in una corsa contro il tempo per sopravvivere, mentre l’orrore si scatena intorno a lui. Reboot della saga tratta dal videogioco, diretto da Zach Cregger.",
    "Un tranquillo funerale di famiglia": "Nel giorno del funerale del patriarca della famiglia Mancuso, la cerimonia solenne si trasforma in una catena di rivelazioni inattese ed equivoci grotteschi. Al centro i due figli, Daria e Riccardo, alle prese con segreti e rancori mai sopiti. Commedia nera di Massimiliano Bruno, ispirata a Funeral Party.",
    "Dracula di Bram Stoker 4K": "Il conte Dracula lascia la Transilvania per Londra, dove crede di aver ritrovato in Mina la donna che amava secoli prima. Il professor Van Helsing e un gruppo di uomini cercano di fermarlo. Il film di Francis Ford Coppola, in versione restaurata 4K.",
    "Prima della rivoluzione": "Fabrizio, giovane borghese di Parma, è diviso tra gli ideali marxisti e il legame con la zia Gina, giovane e inquieta. Alla fine sceglie la via della sua classe. Film di Bernardo Bertolucci del 1964.",
    "The Bibi Files": "Documentario sulle indagini per corruzione a carico del primo ministro israeliano Benjamin Netanyahu, costruito anche con i filmati degli interrogatori della polizia.",
    "Strange Journey: The Story of Rocky Horror": "Documentario sulla storia del musical The Rocky Horror Show e del film cult The Rocky Horror Picture Show, tra ricordi, interviste e il fenomeno dei fan.",
    "Carla Lonzi - Dentro e fuori dal mondo": "Documentario sulla vita e sul pensiero di Carla Lonzi, critica d’arte e figura chiave del femminismo italiano.",
    "Tomorrow X Together world tour Act: tomorrow": "Film-concerto sul tour mondiale del gruppo K-pop Tomorrow X Together.",
    "Enhypen World Tour Blood Saga": "Film-concerto sul tour mondiale del gruppo K-pop Enhypen.",
    "La bambola": "Rémi vende metri di finto prato e non ha mai superato l’abbandono della donna che amava: per compagnia ha una bambola, Audrey. Quando arriva una nuova collega, Audrey prende vita, e Rémi si trova a gestire due donne in carne e ossa, in casa e al lavoro. Commedia francese surreale.",
    "Il dottor Stranamore, ovvero: come imparai a non preoccuparmi e ad amare la bomba": "Un generale americano impazzito ordina un attacco nucleare all’Unione Sovietica. Il presidente cerca di fermarlo nella War Room, ma la catastrofe sembra inevitabile. Classico satirico di Stanley Kubrick del 1964.",
    "Per silenzio e vento": "Documentario di Marco Zuin con lo scrittore Matteo Righetto. Racconta il legame spirituale tra l’uomo e la montagna, tra le Dolomiti e altri luoghi alpini, e propone l’alpinismo non come conquista ma come forma di ascolto.",
    "Era meglio domani": "Commedia francese di viaggio nel tempo, diretta da Vinciane Millereau. I protagonisti si ritrovano nel futuro e restano disorientati non solo dalle novità, ma dal ribaltamento dei loro equilibri: il film mette a confronto ciò che abbiamo perso e ciò che abbiamo conquistato, a cominciare dal ruolo delle donne.",
    "Paw Patrol - Missione Dinosauri": "Nuova avventura animata per i più piccoli: i cuccioli della squadra PAW Patrol si trovano a vivere una missione a tema dinosauri.",
    "Coco": "Miguel, un ragazzino messicano che sogna di fare il musicista nonostante il divieto della famiglia, finisce per errore nella Terra dei Morti durante il Día de los Muertos. Per tornare tra i vivi deve scoprire il segreto del suo antenato. Classico Pixar del 2017, tornato in sala.",
    "Michael": "Film biografico su Michael Jackson, dagli esordi con i Jackson 5 fino all’ascesa a icona mondiale della musica. Diretto da Antoine Fuqua.",
    "Bts World Tour Arirang in Busan - Live Viewing": "Concerto dei BTS a Busan, tappa del tour mondiale Arirang, trasmesso nei cinema in diretta."
  },
  CAST: {
    "Matrix": "Keanu Reeves, Laurence Fishburne, Carrie-Anne Moss, Hugo Weaving",
    "Resident Evil": "Austin Abrams, Paul Walter Hauser, Zach Cherry, Kali Reis",
    "Un tranquillo funerale di famiglia": "Claudia Pandolfi, Pietro Sermonti, Diego Abatantuono, Stefania Sandrelli, Stefano Fresi",
    "Dracula di Bram Stoker 4K": "Gary Oldman, Winona Ryder, Anthony Hopkins, Keanu Reeves",
    "Prima della rivoluzione": "Adriana Asti, Francesco Barilli",
    "The Bibi Files": "documentario, senza cast",
    "Strange Journey: The Story of Rocky Horror": "documentario, senza cast",
    "Carla Lonzi - Dentro e fuori dal mondo": "documentario, senza cast",
    "Tomorrow X Together world tour Act: tomorrow": "Tomorrow X Together",
    "Enhypen World Tour Blood Saga": "Enhypen",
    "Maigret, l'amore e la morte": "Denis Podalydès",
    "La bambola": "Vincent Macaigne, Cécile De France",
    "Il dottor Stranamore, ovvero: come imparai a non preoccuparmi e ad amare la bomba": "Peter Sellers, George C. Scott, Sterling Hayden",
    "Per silenzio e vento": "documentario, con Matteo Righetto",
    "Era meglio domani": "Elsa Zylberstein, Didier Bourdon, Mathilde Le Borgne",
    "Coco": "voci originali di Anthony Gonzalez, Gael García Bernal, Benjamin Bratt, Alanna Ubach",
    "Michael": "Jaafar Jackson, Colman Domingo, Nia Long, Miles Teller, Laura Harrier",
    "Bts World Tour Arirang in Busan - Live Viewing": "BTS"
  },
  CRIT: {
    "La bambola": 2.38,
    "Il dottor Stranamore, ovvero: come imparai a non preoccuparmi e ad amare la bomba": 4.25
  }
};
