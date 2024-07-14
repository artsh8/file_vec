Демо-проект по созданию эмбедингов на основе загруженных файлов *.txt с целью реализации контекстного поиска по этим файлам.

Для создания эмбедингов используется векторная база данных [txtai](https://github.com/neuml/txtai) с языковой моделью [snagbreac/russian-reverse-dictionary-semsearch](https://huggingface.co/snagbreac/russian-reverse-dictionary-semsearch). БД уже инициализирована в образе (вес образа с пустой БД ~ 8.5GB), поэтому при запуске контейнера будет запущен только веб-сервер.

Для запуска из докер-образа необходимо выполнить команду:

`docker run --name file-vec -p 5000:5000 -e FLSK_SECRET_KEY="указать произвольный набор символов" artsh8/file-vec`