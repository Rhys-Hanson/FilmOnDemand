export interface CastMember {
  name: string;
  character: string;
  imageUrl: string;
}

export interface Movie {
  id: string;
  title: string;
  posterUrl: string;
  description: string;
  cast: string[]; // Keeping for backward compatibility
  castList: CastMember[];
  rtScore: number;
  imdbScore: number;
  metacriticScore: number;
  summary: string;
  genre: string[];
  year: number;
  youtubeId: string;
  maturityRating: string;
  runtime: string;
  streamingServices?: string[];
}

export const MOVIE_DATA: Movie[] = [
  {
    id: "m1",
    title: "Dune: Part Two",
    posterUrl: "https://image.tmdb.org/t/p/original/1pdfLvkbY9ohJlCjQH2IGcgTow2.jpg",
    description: "Paul Atreides unites with Chani and the Fremen while on a warpath of revenge against the conspirators who destroyed his family.",
    cast: ["Timothée Chalamet", "Zendaya", "Rebecca Ferguson", "Javier Bardem"],
    castList: [
      { name: "Timothée Chalamet", character: "Paul Atreides", imageUrl: "https://image.tmdb.org/t/p/w185/BE2sdjpgsa2rNTFa66f7upkaOP.jpg" },
      { name: "Zendaya", character: "Chani", imageUrl: "https://image.tmdb.org/t/p/w185/3WbA8AEEwzHk211PzXg8Yw1Bq1z.jpg" },
      { name: "Rebecca Ferguson", character: "Lady Jessica", imageUrl: "https://image.tmdb.org/t/p/w185/lJloTOheuQSirDPkxDNV1ShEQiq.jpg" },
      { name: "Javier Bardem", character: "Stilgar", imageUrl: "https://image.tmdb.org/t/p/w185/gA1H1kZqA183L5u2nBq00b6o1iT.jpg" }
    ],
    rtScore: 93,
    imdbScore: 8.8,
    metacriticScore: 79,
    summary: "A visually stunning sci-fi epic that expands the universe of Arrakis.",
    genre: ["Sci-Fi", "Adventure", "Action"],
    year: 2024,
    youtubeId: "Way9Dexny3w",
    maturityRating: "PG-13",
    runtime: "2h 46m",
    streamingServices: ["Max", "Apple TV+"]
  },
  {
    id: "m2",
    title: "Oppenheimer",
    posterUrl: "https://image.tmdb.org/t/p/original/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg",
    description: "The story of American scientist J. Robert Oppenheimer and his role in the development of the atomic bomb.",
    cast: ["Cillian Murphy", "Emily Blunt", "Matt Damon", "Robert Downey Jr."],
    castList: [
      { name: "Cillian Murphy", character: "J. Robert Oppenheimer", imageUrl: "https://image.tmdb.org/t/p/w185/30Z1XhA72A2X00T2Nsqp21hE2C.jpg" },
      { name: "Emily Blunt", character: "Kitty Oppenheimer", imageUrl: "https://image.tmdb.org/t/p/w185/nPJXaRMvu1h3oq3Vu6DvuVwOfzv.jpg" },
      { name: "Matt Damon", character: "Leslie Groves", imageUrl: "https://image.tmdb.org/t/p/w185/At3JglaDsqX0hktzGj19Z9I9Uv.jpg" },
      { name: "Robert Downey Jr.", character: "Lewis Strauss", imageUrl: "https://image.tmdb.org/t/p/w185/1YjdSym1jTG7xjHSI0yGGWEsw5i.jpg" }
    ],
    rtScore: 93,
    imdbScore: 8.4,
    metacriticScore: 88,
    summary: "A gripping historical drama exploring the moral complexities of the atomic age.",
    genre: ["Biography", "Drama", "History"],
    year: 2023,
    youtubeId: "uYPbbksJxIg",
    maturityRating: "R",
    runtime: "3h 0m",
    streamingServices: ["Peacock", "Prime Video"]
  },
  {
    id: "m3",
    title: "Spider-Man: Across the Spider-Verse",
    posterUrl: "https://image.tmdb.org/t/p/original/8Vt6mWEReuy4Of61Lnj5Xj704m8.jpg",
    description: "Miles Morales catapults across the Multiverse, where he encounters a team of Spider-People charged with protecting its very existence.",
    cast: ["Shameik Moore", "Hailee Steinfeld", "Brian Tyree Henry", "Oscar Isaac"],
    castList: [
      { name: "Shameik Moore", character: "Miles Morales (voice)", imageUrl: "https://image.tmdb.org/t/p/w185/uJNaUT6zFhQzXz7sF25p2g1Vp6.jpg" },
      { name: "Hailee Steinfeld", character: "Gwen Stacy (voice)", imageUrl: "https://image.tmdb.org/t/p/w185/qA1tQhQ2L98O2rNq2z1Q2Vz1Q2V.jpg" },
      { name: "Oscar Isaac", character: "Miguel O'Hara (voice)", imageUrl: "https://image.tmdb.org/t/p/w185/dW5U5yrIIPMaeCYNlsDQilzGbmC.jpg" }
    ],
    rtScore: 95,
    imdbScore: 8.6,
    metacriticScore: 86,
    summary: "An animated masterpiece that pushes the boundaries of visual storytelling.",
    genre: ["Animation", "Action", "Adventure"],
    year: 2023,
    youtubeId: "shW9i6k8cB0",
    maturityRating: "PG",
    runtime: "2h 20m",
    streamingServices: ["Netflix"]
  },
  {
    id: "m4",
    title: "The Batman",
    posterUrl: "https://image.tmdb.org/t/p/original/74xTEgt7R36Fpooo50r9T25onhq.jpg",
    description: "When a sadistic serial killer begins murdering key political figures in Gotham, Batman is forced to investigate the city's hidden corruption.",
    cast: ["Robert Pattinson", "Zoë Kravitz", "Paul Dano", "Jeffrey Wright"],
    castList: [
      { name: "Robert Pattinson", character: "Bruce Wayne / Batman", imageUrl: "https://image.tmdb.org/t/p/w185/8A4PS5iG7GWEAVFftyqMZKl3qcr.jpg" },
      { name: "Zoë Kravitz", character: "Selina Kyle / Catwoman", imageUrl: "https://image.tmdb.org/t/p/w185/zx74cbO8yU70r1U1V8q2q2q2q2q.jpg" },
      { name: "Paul Dano", character: "Edward Nashton / Riddler", imageUrl: "https://image.tmdb.org/t/p/w185/t1q2q2q2q2q2q2q2q2q2q2q2q2q.jpg" }
    ],
    rtScore: 85,
    imdbScore: 7.8,
    metacriticScore: 72,
    summary: "A dark, gritty, and detective-focused take on the Caped Crusader.",
    genre: ["Action", "Crime", "Drama"],
    year: 2022,
    youtubeId: "mqqft2x_Aa4",
    maturityRating: "PG-13",
    runtime: "2h 56m",
    streamingServices: ["Max"]
  },
  {
    id: "m5",
    title: "Everything Everywhere All at Once",
    posterUrl: "https://image.tmdb.org/t/p/original/w3LxiVYdWWRvEVdn5RYq6jIqkb1.jpg",
    description: "An aging Chinese immigrant is swept up in an insane adventure, where she alone can save the world by exploring other universes.",
    cast: ["Michelle Yeoh", "Ke Huy Quan", "Stephanie Hsu", "Jamie Lee Curtis"],
    castList: [
      { name: "Michelle Yeoh", character: "Evelyn Wang", imageUrl: "https://image.tmdb.org/t/p/w185/w1q2q2q2q2q2q2q2q2q2q2q2q2q.jpg" },
      { name: "Ke Huy Quan", character: "Waymond Wang", imageUrl: "https://image.tmdb.org/t/p/w185/w1q2q2q2q2q2q2q2q2q2q2q2q2q.jpg" },
      { name: "Stephanie Hsu", character: "Joy Wang / Jobu Tupaki", imageUrl: "https://image.tmdb.org/t/p/w185/w1q2q2q2q2q2q2q2q2q2q2q2q2q.jpg" }
    ],
    rtScore: 94,
    imdbScore: 7.8,
    metacriticScore: 81,
    summary: "A chaotic, heartfelt, and wildly inventive multiverse journey.",
    genre: ["Action", "Adventure", "Comedy"],
    year: 2022,
    youtubeId: "wxN1T1uxQ2g",
    maturityRating: "R",
    runtime: "2h 19m",
    streamingServices: ["Prime Video", "Paramount+"]
  },
  {
    id: "m6",
    title: "Top Gun: Maverick",
    posterUrl: "https://image.tmdb.org/t/p/original/62HCnUTziyWcpDaBO2i1DX17ljH.jpg",
    description: "After thirty years, Maverick is still pushing the envelope as a top naval aviator, but must confront ghosts of his past when he leads TOP GUN's elite graduates on a mission.",
    cast: ["Tom Cruise", "Miles Teller", "Jennifer Connelly", "Jon Hamm"],
    castList: [
      { name: "Tom Cruise", character: "Capt. Pete 'Maverick' Mitchell", imageUrl: "https://image.tmdb.org/t/p/w185/w1q2q2q2q2q2q2q2q2q2q2q2q2q.jpg" },
      { name: "Miles Teller", character: "Lt. Bradley 'Rooster' Bradshaw", imageUrl: "https://image.tmdb.org/t/p/w185/w1q2q2q2q2q2q2q2q2q2q2q2q2q.jpg" },
      { name: "Jennifer Connelly", character: "Penny Benjamin", imageUrl: "https://image.tmdb.org/t/p/w185/w1q2q2q2q2q2q2q2q2q2q2q2q2q.jpg" }
    ],
    rtScore: 96,
    imdbScore: 8.3,
    metacriticScore: 78,
    summary: "A high-octane legacy sequel that delivers incredible aerial action.",
    genre: ["Action", "Drama"],
    year: 2022,
    youtubeId: "giXco2jaZ_4",
    maturityRating: "PG-13",
    runtime: "2h 10m",
    streamingServices: ["Paramount+", "Prime Video"]
  },
  {
    id: "m7",
    title: "Knives Out",
    posterUrl: "https://image.tmdb.org/t/p/original/pThyQovXQrw2m0s9x82twj48Jq4.jpg",
    description: "A detective investigates the death of a patriarch of an eccentric, combative family.",
    cast: ["Daniel Craig", "Chris Evans", "Ana de Armas", "Jamie Lee Curtis"],
    castList: [
      { name: "Daniel Craig", character: "Benoit Blanc", imageUrl: "https://image.tmdb.org/t/p/w185/w1q2q2q2q2q2q2q2q2q2q2q2q2q.jpg" },
      { name: "Chris Evans", character: "Ransom Drysdale", imageUrl: "https://image.tmdb.org/t/p/w185/w1q2q2q2q2q2q2q2q2q2q2q2q2q.jpg" },
      { name: "Ana de Armas", character: "Marta Cabrera", imageUrl: "https://image.tmdb.org/t/p/w185/w1q2q2q2q2q2q2q2q2q2q2q2q2q.jpg" }
    ],
    rtScore: 97,
    imdbScore: 7.9,
    metacriticScore: 82,
    summary: "A sharp, witty, and thoroughly entertaining modern whodunit.",
    genre: ["Comedy", "Crime", "Drama"],
    year: 2019,
    youtubeId: "qGqiHJTsRkQ",
    maturityRating: "PG-13",
    runtime: "2h 10m",
    streamingServices: ["Netflix"]
  },
  {
    id: "m8",
    title: "Parasite",
    posterUrl: "https://image.tmdb.org/t/p/original/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg",
    description: "Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan.",
    cast: ["Song Kang-ho", "Lee Sun-kyun", "Cho Yeo-jeong", "Choi Woo-shik"],
    castList: [
      { name: "Song Kang-ho", character: "Ki-taek", imageUrl: "https://image.tmdb.org/t/p/w185/w1q2q2q2q2q2q2q2q2q2q2q2q2q.jpg" },
      { name: "Lee Sun-kyun", character: "Dong-ik", imageUrl: "https://image.tmdb.org/t/p/w185/w1q2q2q2q2q2q2q2q2q2q2q2q2q.jpg" },
      { name: "Cho Yeo-jeong", character: "Yeon-gyo", imageUrl: "https://image.tmdb.org/t/p/w185/w1q2q2q2q2q2q2q2q2q2q2q2q2q.jpg" }
    ],
    rtScore: 99,
    imdbScore: 8.5,
    metacriticScore: 96,
    summary: "A masterful, genre-bending thriller about class struggle.",
    genre: ["Drama", "Thriller", "Comedy"],
    year: 2019,
    youtubeId: "5xH0HfJHsaY",
    maturityRating: "R",
    runtime: "2h 12m",
    streamingServices: ["Max", "Hulu"]
  },
  {
    id: "m9",
    title: "Mad Max: Fury Road",
    posterUrl: "https://image.tmdb.org/t/p/original/hA2ple9q4cbBUGRVG37DicvSMkV.jpg",
    description: "In a post-apocalyptic wasteland, a woman rebels against a tyrannical ruler in search for her homeland with the aid of a group of female prisoners, a psychotic worshiper, and a drifter named Max.",
    cast: ["Tom Hardy", "Charlize Theron", "Nicholas Hoult", "Hugh Keays-Byrne"],
    castList: [
      { name: "Tom Hardy", character: "Max Rockatansky", imageUrl: "https://image.tmdb.org/t/p/w185/w1q2q2q2q2q2q2q2q2q2q2q2q2q.jpg" },
      { name: "Charlize Theron", character: "Imperator Furiosa", imageUrl: "https://image.tmdb.org/t/p/w185/w1q2q2q2q2q2q2q2q2q2q2q2q2q.jpg" },
      { name: "Nicholas Hoult", character: "Nux", imageUrl: "https://image.tmdb.org/t/p/w185/w1q2q2q2q2q2q2q2q2q2q2q2q2q.jpg" }
    ],
    rtScore: 97,
    imdbScore: 8.1,
    metacriticScore: 90,
    summary: "A relentless, visually spectacular action masterpiece.",
    genre: ["Action", "Adventure", "Sci-Fi"],
    year: 2015,
    youtubeId: "hEJnMQG9ev8",
    maturityRating: "R",
    runtime: "2h 0m",
    streamingServices: ["Max"]
  },
  {
    id: "m10",
    title: "Inception",
    posterUrl: "https://image.tmdb.org/t/p/original/oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg",
    description: "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.",
    cast: ["Leonardo DiCaprio", "Joseph Gordon-Levitt", "Elliot Page", "Tom Hardy"],
    castList: [
      { name: "Leonardo DiCaprio", character: "Cobb", imageUrl: "https://image.tmdb.org/t/p/w185/w1q2q2q2q2q2q2q2q2q2q2q2q2q.jpg" },
      { name: "Joseph Gordon-Levitt", character: "Arthur", imageUrl: "https://image.tmdb.org/t/p/w185/w1q2q2q2q2q2q2q2q2q2q2q2q2q.jpg" },
      { name: "Elliot Page", character: "Ariadne", imageUrl: "https://image.tmdb.org/t/p/w185/w1q2q2q2q2q2q2q2q2q2q2q2q2q.jpg" }
    ],
    rtScore: 87,
    imdbScore: 8.8,
    metacriticScore: 74,
    summary: "A mind-bending sci-fi heist film that explores the architecture of dreams.",
    genre: ["Action", "Adventure", "Sci-Fi"],
    year: 2010,
    youtubeId: "YoHD9XEInc0",
    maturityRating: "PG-13",
    runtime: "2h 28m",
    streamingServices: ["Hulu", "Prime Video"]
  }
];
