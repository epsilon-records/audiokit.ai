# **AudioKit Brain - Neo4j Graph Schema Specification**

## **1. Overview**

The **AudioKit Brain Graph** is a **knowledge graph** implemented in **Neo4j**, designed to model the **global music ecosystem** with **AI-powered analytics**. This schema integrates **real-time data** from multiple sources, including **SoundCharts, Genius, Spotify, Last.fm, and Chartmetric**, to provide an optimized structure for querying artist collaborations, streaming analytics, audience demographics, and music trends.

This document details the **schema structure**, including **node types, relationships, and property definitions**, to ensure high-performance AI-driven graph operations.

---

## **2. Schema Definition**

The schema consists of **multiple node types** (entities) and **relationships** that define interactions within the music industry.

### **2.1 Node Labels (Entities)**

Each node type represents an **entity** in the music graph and contains **specific attributes** optimized for graph traversal and AI-driven predictions.

| **Label**           | **Description** | **Primary Key** | **Properties** |
|---------------------|----------------|----------------|---------------|
| `Artist`           | Musician or band | `artist_id` | `name`, `genre`, `country`, `popularity_score`, `spotify_id`, `lastfm_id`, `chartmetric_id` |
| `Track`            | Individual song | `track_id` | `title`, `release_date`, `duration`, `bpm`, `key`, `spotify_id`, `chartmetric_id` |
| `Album`            | Collection of tracks | `album_id` | `title`, `release_date`, `spotify_id`, `chartmetric_id` |
| `Chart`            | Music rankings | `chart_id` | `name`, `platform`, `date`, `rankings` |
| `Playlist`         | Curated song list | `playlist_id` | `name`, `platform`, `follower_count`, `spotify_id`, `chartmetric_id` |
| `RadioStation`     | Music broadcast entity | `station_id` | `name`, `frequency`, `country` |
| `Platform`         | Streaming service | `platform_id` | `name`, `type` (e.g., streaming, social), `user_count` |
| `Label`            | Record company | `label_id` | `name`, `country`, `founded_year` |
| `User`             | Listener profile | `user_id` | `username`, `platform`, `listening_history`, `follower_count` |
| `TikTokVideo`      | Short-form music video | `tiktok_id` | `video_url`, `likes_count`, `shares_count` |
| `Lyrics`           | Song lyrics | `lyrics_id` | `text`, `language` |
| `Annotation`       | Explanation of lyrics | `annotation_id` | `content`, `source` |
| `StreamingData`    | Track play statistics | `stream_id` | `stream_count`, `peak_position`, `date` |
| `AudioFeature`     | Acoustic properties of tracks | `feature_id` | `tempo`, `danceability`, `valence`, `instrumentalness` |
| `SocialMetric`     | Social media performance | `social_id` | `platform`, `followers`, `engagement_rate` |
| `Audience`         | Artist listener demographics | `audience_id` | `country`, `age_group`, `gender_distribution` |

---

### **2.2 Relationship Types**

Relationships define **interactions** between nodes and allow **AI-driven queries** for predictions and analysis.

| **Relationship**    | **From → To** | **Description** |
|---------------------|--------------|----------------|
| `PERFORMED`        | `(:Artist) → (:Track)` | Artist performed a song |
| `PRODUCED_BY`      | `(:Track) → (:Artist)` | Song was produced by an artist |
| `FEATURED_ON`      | `(:Track) → (:Playlist)` | Song is part of a playlist |
| `CHARTED_ON`       | `(:Track) → (:Chart)` | Song appeared on a music chart |
| `SIGNED_TO`        | `(:Artist) → (:Label)` | Artist signed to a record label |
| `BELONGS_TO`       | `(:Track) → (:Genre)` | Song classified into a genre |
| `STREAMED_ON`      | `(:Track) → (:Platform)` | Song is available on a platform |
| `BROADCASTED_BY`   | `(:Track) → (:RadioStation)` | Song played on a radio station |
| `FEATURED_IN`      | `(:Track) → (:TikTokVideo)` | Song used in TikTok content |
| `HAS_LYRICS`       | `(:Track) → (:Lyrics)` | Lyrics attached to a track |
| `ANNOTATED_BY`     | `(:Lyrics) → (:Annotation)` | Lyrics have an explanation |
| `HAS_STREAMS`      | `(:Track) → (:StreamingData)` | Track has streaming metrics |
| `HAS_FEATURES`     | `(:Track) → (:AudioFeature)` | Track has audio analysis |
| `LIKED_BY`         | `(:Track) → (:User)` | User liked or saved this track |
| `FOLLOWS`          | `(:User) → (:Artist)` | User follows an artist |
| `LISTENS_TO`       | `(:User) → (:Track)` | User streamed this track |
| `SCROBBLED`        | `(:User) → (:Scrobble)` | User listened to a track on Last.fm |
| `TAGGED_AS`        | `(:Track) → (:Tag)` | Song tagged with descriptive metadata |
| `SIMILAR_TO`       | `(:Artist) → (:SimilarArtist)` | Similar artists detected |
| `HAS_SOCIAL_METRICS` | `(:Artist) → (:SocialMetric)` | Artist has social media metrics |
| `HAS_AUDIENCE`     | `(:Artist) → (:Audience)` | Artist has audience demographics |

---

## **3. Query Optimization & AI Workflows**

### **3.1 AI-Powered Query Optimizations**

The **AudioKit Brain Graph** is optimized for **high-speed graph traversal** with:

- **Indexing on primary keys** (`artist_id`, `track_id`, etc.)
- **Full-text search indexes** for lyrics and annotations
- **Graph projections for fast recommendation queries**

### **3.2 AI Query Examples**

#### **Find an artist's most streamed songs**

```cypher
MATCH (a:Artist {name: "Kendrick Lamar"})-[:PERFORMED]->(t:Track)-[:HAS_STREAMS]->(s:StreamingData)
RETURN t.title, s.stream_count ORDER BY s.stream_count DESC;
```

#### **Find similar artists using Last.fm data**

```cypher
MATCH (a:Artist {name: "Kendrick Lamar"})-[:SIMILAR_TO]->(s:Artist)
RETURN s.name;
```

#### **Retrieve audience demographics for an artist**

```cypher
MATCH (a:Artist {name: "Kendrick Lamar"})-[:HAS_AUDIENCE]->(aud:Audience)
RETURN aud.country, aud.age_group, aud.gender_distribution;
```

---

## **4. Conclusion**

The **AudioKit Brain Graph** provides an **AI-driven, highly scalable** music knowledge graph that enables **complex data analytics, trend analysis, and recommendation systems**. This schema is designed for **fast retrieval, real-time insights, and deep industry analysis**.
