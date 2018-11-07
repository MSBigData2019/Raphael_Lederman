package com.sparkProject

import org.apache.spark.SparkConf
import org.apache.spark.sql.{DataFrame, SaveMode, SparkSession}
import org.apache.spark.ml.feature.{RegexTokenizer, Tokenizer, VectorAssembler, StopWordsRemover, CountVectorizer, IDF, StringIndexer, OneHotEncoder}
import org.apache.spark.ml.classification.{LogisticRegression, RandomForestClassifier}
import org.apache.spark.ml.evaluation.MulticlassClassificationEvaluator
import org.apache.spark.ml.{Pipeline, PipelineModel}
import org.apache.spark.ml.tuning.{TrainValidationSplit, ParamGridBuilder}


object Trainer {

  def main(args: Array[String]): Unit = {

    val conf = new SparkConf().setAll(Map(
      "spark.scheduler.mode" -> "FIFO",
      "spark.speculation" -> "false",
      "spark.reducer.maxSizeInFlight" -> "48m",
      "spark.serializer" -> "org.apache.spark.serializer.KryoSerializer",
      "spark.kryoserializer.buffer.max" -> "1g",
      "spark.shuffle.file.buffer" -> "32k",
      "spark.default.parallelism" -> "12",
      "spark.sql.shuffle.partitions" -> "12",
      "spark.driver.maxResultSize" -> "2g"
    ))

    val spark = SparkSession
      .builder
      .config(conf)
      .appName("TP_spark")
      .getOrCreate()

    import spark.implicits._


    /*******************************************************************************
      *
      *       TP 3
      *
      *       - lire le fichier sauvegarder précédemment
      *       - construire les Stages du pipeline, puis les assembler
      *       - trouver les meilleurs hyperparamètres pour l'entraînement du pipeline avec une grid-search
      *       - Sauvegarder le pipeline entraîné
      *
      *       if problems with unimported modules => sbt plugins update
      *
      ********************************************************************************/


    /* 1 - CHARGEMENT DES DONNEES
      * Chargement des données préparées dans par le Preprocessor.
      */

    val df: DataFrame = spark
      .read.parquet("/Users/RaphaelLederman/Library/Mobile Documents/com~apple~CloudDocs/MasterDS/Telecom_Cours/Hadoop_INF729/Main/Spark/TP2/prepared_trainingset")

    /* 2 -  TRAITEMENT DES DONNEES TEXTUELLES
      * La variable 'text' n'est pas utilisable telle quelle par les algorithmes de ML (car non numérique)
      * On applique donc l'algorithme TF-IDF afin de convertir cette variable en donnée numérique.
      */

    // Stage 1 : Tokenizer
    val tokenizer = new RegexTokenizer()
      .setPattern("\\W+")
      .setGaps(true)
      .setInputCol("text")
      .setOutputCol("tokens")

    // Stage 2 : StopWordsRemover
    val remover = new StopWordsRemover()
      .setInputCol(tokenizer.getOutputCol)
      .setOutputCol("filtered")

    // Stage 3 : CountVectorizer
    val vectorizer = new CountVectorizer()
      .setInputCol(remover.getOutputCol)
      .setOutputCol("vectorized")

    // Stage 4: IDF
    val idf = new IDF()
      .setInputCol(vectorizer.getOutputCol)
      .setOutputCol("tfidf")


    /* 3 - TRAITEMENT DES DONNEES CATEGORIQUE
      * On cherche à convertir les variables catégorielles ['country2','currency2]
      * en variables numériques
      */

    // Stage 5: StringIndexer  sur la variable 'country2'
    val indexer_country = new StringIndexer()
      .setInputCol("country2")
      .setOutputCol("country_indexed")
      .setHandleInvalid("skip")

    // Stage 6: StringIndexer sur la variable 'currency2'
    val indexer_currency = new StringIndexer()
      .setInputCol("currency2")
      .setOutputCol("currency_indexed")
      .setHandleInvalid("skip")

    // Stage 7: OneHotEncoder sur la variable 'country2'
    val encoder_country = new OneHotEncoder()
      .setInputCol("country_indexed")
      .setOutputCol("country_onehot")


    // Stage 8: OneHotEncoder sur la variable 'currency2'
    val encoder_currency = new OneHotEncoder()
      .setInputCol("currency_indexed")
      .setOutputCol("currency_onehot")

    /* 4 - MISE AU FORMAT SPARK.ML
      * Les libraries spark.ML necessitent un format de données particulier:
      * les colonnes utilisées en input des modèle (features) doivent être regroupées dans une seule colonne
      */

    // Stage 9: Création de la colonne 'features'
    val assembler = new VectorAssembler()
      .setInputCols(Array("tfidf", "days_campaign", "hours_prepa", "goal", "country_onehot", "currency_onehot"))
      .setOutputCol("features")

    // Stage 10: Classification par regression logistique
    val lr = new LogisticRegression()
      .setElasticNetParam(0.0)
      .setFitIntercept(true)
      .setFeaturesCol("features")
      .setLabelCol("final_status")
      .setStandardization(true)
      .setPredictionCol("predictions")
      .setRawPredictionCol("raw_predictions")
      .setThresholds(Array(0.7, 0.3))
      .setTol(1.0e-6)
      .setMaxIter(300)

    val rf = new RandomForestClassifier()
      .setFeaturesCol("features")
      .setLabelCol("final_status")
      .setPredictionCol("predictions")
      .setRawPredictionCol("raw_predictions")
      .setNumTrees(20)
      .setMaxDepth(5)
      .setMaxBins(32)

    // Création du Pipeline
    val pipeline = new Pipeline()
      .setStages(Array(tokenizer, remover, vectorizer, idf, indexer_country, indexer_currency, encoder_country, encoder_currency, assembler, rf))

    /* 5 - ENTRAINEMENT ET TUNNING DU MODELE
      * Séparation des données aléatoirement en un training set (90%) et un test set (10%)
      * Puis entrainement du classifieur et réglage des hyper-paramètres de l'algorithme
      */

    // Split des données en Training Set et Test Set
    val Array(training, test) = df
      .randomSplit(Array(0.9,0.1), seed=11L)

    // Grille de valeur des Hyper-paramètres à tester
    val paramGrid = new ParamGridBuilder()
      .addGrid(lr.regParam, Array(10e-8, 10e-6, 10e-4, 10e-2))
      .addGrid(vectorizer.minDF, 55.0.to(95.0).by(20).toArray)
      .build()

    val paramGrid_rf = new ParamGridBuilder()
      .addGrid(rf.maxDepth, Array(10,25, 50))
      .addGrid(rf.numTrees, Array(10, 20, 30))
      .build()

    // Evaluation par le F1 Score
    val evaluator = new MulticlassClassificationEvaluator()
      .setLabelCol("final_status")
      .setPredictionCol("predictions")
      .setMetricName("f1")

    // Choix des Hyper-paramètres optimaux
    val TVS = new TrainValidationSplit()
      .setEstimator(pipeline)
      .setEvaluator(evaluator)
      .setEstimatorParamMaps(paramGrid)
      .setTrainRatio(0.7)

    // Application du modèle optimal sur le training set
    val model_tuned = TVS.fit(training)
    
    // Calcul des predictions du modèle optimal
    val dfPrediction = model_tuned
      .transform(test)
      .select("features","final_status", "predictions", "raw_predictions")

    // Calcul du F1 Score
    val metrics = evaluator.evaluate(dfPrediction)
    println("F1 Score du modèle sur le Test set : " + metrics)

    // Affiche les predictions
    dfPrediction.groupBy("final_status","predictions").count.show()

  }
}
