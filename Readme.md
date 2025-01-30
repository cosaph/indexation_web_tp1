# 📚 Projet d'Indexation Web - ENSAI 2025

Ce projet est composé de trois travaux pratiques (TP) qui visent à développer un système complet de crawling, d'indexation et de recherche sur le web. Chaque TP est conçu pour vous permettre de comprendre et de mettre en pratique les concepts clés de l'indexation web.

---

## 🕷️ TP1 - Développement d'un Web Crawler

### Objectif 🎯
Créer un crawler en Python qui explore les pages d'un site web en priorisant certaines pages, notamment les pages de produits.

### Fonctionnalités clés 🔑
- Extraction du **titre**, du **premier paragraphe** et des **liens internes**.
- Priorisation des liens contenant le mot-clé `product`.
- Stockage des données dans un fichier JSON.
- Arrêt après avoir visité **50 pages**.

### Étapes 🚶‍♂️
1. **Configuration initiale** : Installation des bibliothèques nécessaires et mise en place de la structure du projet.
2. **Extraction du contenu** : Parsing du HTML et extraction des informations.
3. **Logique de crawling** : Implémentation d'une file d'attente et d'un système de priorité.
4. **Stockage des données** : Sauvegarde des résultats dans un fichier JSON.
5. **Tests et optimisation** : Gestion des erreurs et amélioration du code.

### Livrable 📄
Un script Python qui prend en entrée une URL de départ et produit un fichier JSON contenant les informations extraites.

---

## 📂 TP2 - Développement d'Index

### Objectif 🎯
Créer différents types d'index à partir d'un jeu de données de produits e-commerce pour préparer la construction d'un moteur de recherche.

### Fonctionnalités clés 🔑
- Création d'index inversés pour le **titre** et la **description**.
- Index des **reviews** (nombre total, note moyenne, dernière note).
- Index des **features** (marque, origine, etc.).
- Index de **position** pour le titre et la description.

### Étapes 🚶‍♂️
1. **Lecture et traitement des URLs** : Extraction des informations des URLs.
2. **Filtrage des documents** : Création des index inversés.
3. **Index des reviews** : Stockage des informations non textuelles.
4. **Index des features** : Traitement des features comme des champs textuels.
5. **Index de position** : Ajout des informations de position dans les index.

### Livrable 📄
Un script Python contenant les fonctions de création, sauvegarde et chargement des index, ainsi qu'un fichier `README.md` détaillant la structure des index et les choix techniques.

---

## 🔍 TP3 - Moteur de Recherche

### Objectif 🎯
Développer un moteur de recherche qui utilise les index créés précédemment pour retourner et classer des résultats pertinents.

### Fonctionnalités clés 🔑
- **Tokenization** et **normalisation** des requêtes.
- **Augmentation des requêtes** avec des synonymes (par exemple pour l'origine des produits).
- **Filtrage des documents** : Vérification de la présence des tokens dans les documents.
- **Ranking** : Calcul des scores de pertinence en utilisant BM25, match exact et d'autres signaux.
- **Stockage des résultats** : Formatage des résultats en JSON.

### Étapes 🚶‍♂️
1. **Lecture et préparation** : Chargement des index et mise en place des fonctions de tokenization.
2. **Filtrage des documents** : Implémentation des fonctions de traitement de requête.
3. **Ranking** : Calcul des scores de pertinence et combinaison des signaux.
4. **Tests et optimisation** : Ajustement des poids et des paramètres.

### Livrable 📄
Un script Python qui produit un fichier JSON contenant les résultats de recherche, ainsi que des métadonnées (nombre total de documents, documents filtrés, etc.).


---


## 🚀 Comment Lancer le Projet

1. **TP1** : Exécutez le script `main.py` avec l'URL de départ et le nombre maximum de pages à visiter.
2. **TP2** : Exécutez le script `create_index.py` pour créer les index à partir du fichier JSONL.
3. **TP3** : Exécutez le script `tp3.py` pour lancer le moteur de recherche et tester les requêtes.

---

## 📜 Contributrice (? pas Français ? la langue française est sexiste aussi)

Coralie Cottet