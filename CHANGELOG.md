# [0.11.0](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/compare/v0.10.0...v0.11.0) (2026-06-17)


### Bug Fixes

* add controls dialog ([9dd4480](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/9dd4480c583967c1cdf0ddd52278dec28a39d9d5))


### Features

* **audio:** add prev/next keyboard control ([612f166](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/612f166584b1aecfd2f081a5238db186167a37cc))


### Performance Improvements

* improve use of constants, remove useless methods and tests, improve code readability ([f299cc4](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/f299cc4e32eaa881f27d27f71a5454655ac2be7b))
* move gravity tick handling in game_screen from tetris model ([1c7ed16](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/1c7ed16b9827c5e087d15c82d6fac4bddc220d9e))

# [0.10.0](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/compare/v0.9.3...v0.10.0) (2026-06-07)


### Bug Fixes

* **view/widgets:** increase podium card heights to prevent content clipping ([8b9394e](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/8b9394e7fd33c65a35d7aa973a3a67df2ce4962a)), closes [#3](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/issues/3) [#2](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/issues/2)
* **view/widgets:** use MaterialIcons star glyph for medal symbols in TopPlayerCard ([5267ac7](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/5267ac793b129f8483d0ce7cc1f5e106edfafdc3))


### Features

* **view/widgets:** add LeaderboardRow card widget ([3637924](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/36379240659274cdba75e290ab987da012fe45be))
* **view/widgets:** add TopPlayerCard widget for podium top-3 ([9799116](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/97991167860d24729577c5fdd7d5c38333a75cf8))
* **view:** highlight current-player rows in leaderboard ([ec60139](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/ec601390ac20145833c4b05f44fb684a88130bd9))
* **view:** rebuild LeaderboardScreen with card layout and tier sections ([6f981ea](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/6f981ea78bbc48a4429f14c14883cca3646ea99b))
* **view:** show rank-change indicator on leaderboard rows ([cd57750](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/cd577503362b03c240e5b17204917a9a11968026))

## [0.9.3](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/compare/v0.9.2...v0.9.3) (2026-05-19)


### Bug Fixes

* **settings:** toggle music from settings ([f6490ce](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/f6490ce7f296af7f7b31169f1b99a66f1e539547))

## [0.9.2](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/compare/v0.9.1...v0.9.2) (2026-05-19)


### Bug Fixes

* **dialog:** disable screen behind overlay ([d16835b](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/d16835b8eda11a1fda628b150466cbfacbd30f3c))
* **menu_screen:** buttons repositioning and settings dialog creation ([1ae1d1e](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/1ae1d1e2e83aa3c5c692c2e35df21950f1876460))

## [0.9.1](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/compare/v0.9.0...v0.9.1) (2026-05-19)


### Bug Fixes

* reset stats after the score is saved ([3771f32](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/3771f3280348aa8a966311c5ccb1868119580d00))

# [0.9.0](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/compare/v0.8.0...v0.9.0) (2026-04-24)


### Bug Fixes

* **Audio Controller:** discover all songs in the path, play the queue in loop ([c374515](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/c374515dab8b203c10feb9f1e10216ae8a838266))
* **Audio Controller:** make silent_controller tests correct ([1b0ea3b](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/1b0ea3b0f4568c3aa3514f9e8518e831023526b2))
* remove pause overlay, improve code and perf ([4ed253d](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/4ed253d6b40a407c3096ad45baf9b9286317036b))


### Features

* **audio:** add IAudioController interface and KivyAudioController singleton ([0b02791](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/0b02791208aa4cebec6eedfb351cfbe4339ae18a))
* **leaderboard:** add CsvLeaderboardRepository singleton ([a4b0498](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/a4b0498bf9767f86bfdb9aa01e56974256c75ac2))
* **leaderboard:** add LeaderboardEntry dataclass and ILeaderboardRepository interface ([5c006d2](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/5c006d296118894879fe9f0f98383b111306caed))
* **view:** add leaderboard button to menu and wire navigation in app ([99cfdd1](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/99cfdd1d0e77ba5fbb4ff26d7bf25bb03e5b56f1))
* **view:** add LeaderboardScreen and i18n keys ([0aa61e9](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/0aa61e9da12c7606dfecf5adfd2b99d41931be14))
* **view:** add music toggle button and 'm' shortcut to game screen ([b2f4323](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/b2f432344947ba1ca0f87de35e66415ec82017c8))
* **view:** add volume slider to menu ([df22674](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/df226749259ac2f73ffd6474485b328816d21586))
* **view:** show name input on game over and save to leaderboard ([cfa3428](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/cfa3428730f9956da121eeb31ebf0ad6faa44886))


### Performance Improvements

* move assets and locales in root folder, define absolute local path ([6e8647a](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/6e8647af074f6ae6d702d405a5ea48313f4c27ca))

# [0.8.0](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/compare/v0.7.5...v0.8.0) (2026-04-23)


### Bug Fixes

* **game screen:** centered the elements and made the game screen responsive ([214f416](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/214f416461d61decd17dfa7939da635f4f1ae581))
* **game screen:** split the screen in three columns to reposition the elements ([684067c](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/684067cf294e6ba93ac7f9aad6ab373d4cb7ab21))
* replace BLOCK_COLOURS with EMPTY_COLOUR, update tests ([ebab99f](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/ebab99fe960465b7ddf22a3b0bea0beee6f1adf3))
* reset stats and pieces in a game ([4e7d87c](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/4e7d87c2767d0992d71f6f60c575f73e163a5443))
* **tetris:** enable wall-kick ([e2835a5](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/e2835a582ff07e3c1ee3e136bb10bbca285ffba9))
* **ui:** add background to game screen ([5ebbc5d](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/5ebbc5dc7affb67884462194fbe4aef214f8a803))
* **ui:** add board container, fix hold preview ([4cf53ca](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/4cf53ca0b9052c5005b92ebdde2ef4f5d21bf9c4))
* **ui:** fill board background ([3bd8799](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/3bd879917ded90c0147661fefd5d7174eb1ab605))
* **ui:** refactor game over dialog overlay ([de3eb66](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/de3eb6690f77e8f6fa14a21ec7309ea354848532))
* **ui:** refactor pause dialog overlay ([055af22](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/055af22db6e4664c0f6a07433775f59c4cac8562))
* **ui:** refactor quit dialog overlay ([29dd882](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/29dd8829c1d06bf9bece7ae67878c3408bccfe77))
* **view:** fix border radius inconsistency and document is_animating setter ([9a95510](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/9a955109af70a15745da35ae3ed0a9b37074b17a))
* **view:** restore white flash color and improve is_animating docstring ([3930b02](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/3930b024daab0d1eb616b4223e55baa8bf2052fd))


### Features

* **ui:** add icons in tetrominoes squares ([2859e97](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/2859e97edff61b95d5df728e53dbb991c3549c01))
* **view:** add BoardWidget with rendering and animation logic ([89532cb](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/89532cb39005c04090953885a7ed014146d364ad))
* **view:** export BoardWidget from widgets package ([a5d1b13](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/a5d1b1342903c2b21aa5974656fe2a4486ffe505))

## [0.7.5](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/compare/v0.7.4...v0.7.5) (2026-03-28)


### Bug Fixes

* replace buttons text with icons ([e972679](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/e972679f6cda5eafc4ec5d7a0c6f4aa5cd776492))

## [0.7.4](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/compare/v0.7.3...v0.7.4) (2026-03-27)


### Bug Fixes

* add countdown on try again and resume ([f1cdd5f](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/f1cdd5f8373c0ec11b850bfbcbb380bd1f7d67ae))
* **model:** use official time formula for tick_interval ([fe6addf](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/fe6addf0a3270268fb21876633998e8d00f02448))

## [0.7.3](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/compare/v0.7.2...v0.7.3) (2026-03-27)


### Bug Fixes

* **Game Screen:** add quit keyboard shortcut ([8005dbf](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/8005dbf7ec34a1395cad717f872b57f8c4660e27))
* **game screen:** animation on lines cleared ([4d4dd10](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/4d4dd10ad538e15da0c1ede2795c4b3ee47dc2bd))
* **Game Screen:** refresh labels when shown ([be214a8](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/be214a8fa9dc2f4f93ff6578b9afda4d438b7289))


### Performance Improvements

* move try again handler from app.py to game_screen.py ([0f6dab1](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/0f6dab14bfbb369d629f87d78ed904fe7c11fe39))

## [0.7.2](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/compare/v0.7.1...v0.7.2) (2026-03-26)


### Bug Fixes

* **game_screen:** add the quit button to end the current game ([79b3f80](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/79b3f80d7601745859b53398953ea7ffba2293a6))
* **game_screen:** add the try again button to start a new game ([8b1b4d4](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/8b1b4d4e548f7037c78fb3c83ae0a206ccb76095))
* **menu_screen:** add quit button to exit the application ([7b4797b](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/7b4797bafbd620386b22de1a7264f11651f9aade))

## [0.7.1](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/compare/v0.7.0...v0.7.1) (2026-03-26)


### Bug Fixes

* when lines cleared, show them being cleared with a timeout among them ([c10e586](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/c10e586014e841b005fc78c486279577a8a2d4e0))

# [0.7.0](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/compare/v0.6.0...v0.7.0) (2026-03-26)


### Features

* **factory:** add BagTetrominoFactory with 7-bag algorithm ([bf5c878](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/bf5c87873379b8b7446bbbd63970a80e30fdfffa))
* **factory:** add ITetrominoFactory interface ([1005718](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/1005718732271ba9e098cc5e72796b7d3035aaad))
* **factory:** wire ITetrominoFactory into Tetris, replace monkeypatching in tests ([972b9db](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/972b9db718f207fc28693a91d29179f76912e475))


### Performance Improvements

* **test:** increase sleep ([00d67b0](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/00d67b011b0b898cee3c2b9954669b4527176199))

# [0.6.0](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/compare/v0.5.0...v0.6.0) (2026-03-26)


### Features

* **i18n:** add python-i18n locale YAML files (en, it) ([4387836](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/4387836aa9ae2843682019b66630654dfb426a4e))
* **i18n:** configure python-i18n in TetrisApp, remove I18n instance ([941749c](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/941749cfc1862a24b51ea047393cc1762f1625e5))
* **i18n:** migrate GameScreen to python-i18n direct API ([0718fe0](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/0718fe050e20e77340d310a31ba5da37096d7cf7))
* **i18n:** migrate MenuScreen to python-i18n direct API ([87f9047](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/87f90474b3fd1ff2781051ffea858dd9e8f35b50))
* **i18n:** remove custom I18n class and i18n tests ([4ae3334](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/4ae3334b36cd8801e287fb0f0115f9fc69eb6a0c))

# [0.5.0](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/compare/v0.4.0...v0.5.0) (2026-03-26)


### Bug Fixes

* errors from static analysis ([a90a5c9](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/a90a5c9b207b84d8377f5993241799b58a530bb9))


### Features

* **view:** add BlockRenderer with image-to-integer mapping ([ed647ab](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/ed647abf6daaa65d9659f900856389e7872c6792))
* **view:** add IView interface and i18n module ([23993c0](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/23993c04acb0fdb8376c19d3c47021eea6ce0a5e))
* **view:** add TetrisApp entry point and screen navigation ([7ed2fc6](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/7ed2fc6399eb2ef57778486432e34455f875dfa7))
* **view:** implement GameScreen layout, board rendering, Observer events and keyboard input ([a841775](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/a84177583c451baac71bd05376fa7e7a2763a1af))
* **view:** implement MenuScreen with language selector ([310e65b](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/310e65b8a986fd2501ec1976a9735ed861ea7acf))
* wire main() entry point to TetrisApp ([295742d](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/295742d4aaf7239f4e35ec0b20cdf489d3663761))

# [0.4.0](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/compare/v0.3.2...v0.4.0) (2026-03-11)


### Features

* **model:** implement Board class ([4cce391](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/4cce39134dd03c799e89cac221b2f22a16e93886))
* **model:** implement Tetris class ([6e1f41f](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/6e1f41fb05cda00d295a4397e2d89166b94447b4))


### Performance Improvements

* check if piece movement is valid in move method ([384b241](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/384b2418831219a15c1400e2316b3e57896932dc))
* improve code optimization ([a21fb06](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/a21fb061fc975038bd349427b29fff63bf819fe0))
* **test:** increase test coverage ([2b69f61](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/2b69f61d97f35892e47d2655db38a8900f343f85))

## [0.3.2](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/compare/v0.3.1...v0.3.2) (2026-03-11)


### Bug Fixes

* **devops:** add configuration to Dependabot ([8a6e773](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/8a6e773a7be74a3b9c998e7a9a1437b825489029))

## [0.3.1](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/compare/v0.3.0...v0.3.1) (2026-03-10)


### Bug Fixes

* **model:** update all dependencies for security issues ([cd13327](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/cd133272bb8e5c96ec074046753d11d2a18c7d9f))

# [0.3.0](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/compare/v0.2.0...v0.3.0) (2026-03-10)


### Bug Fixes

* change ShapeType number coding for future ui recognition ([7421f52](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/7421f52fb53349e27229a59a19a1f15619fc2483))
* define event type constants ([69fe789](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/69fe789530fa9c4f3ff7c4c5e3749b799ed5b8f3))
* define event type constants ([e8b7d11](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/e8b7d11498033253504589b0d26a8f2863dcae05))
* shapetype definition ([04a8547](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/04a8547e07c581d46bb80021eea7161ab9189920))


### Features

* define model interfaces ([0b1e46f](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/0b1e46f643802d5ae1691debbedf9db7cb1f14de))

# [0.2.0](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/compare/v0.1.3...v0.2.0) (2026-03-08)


### Features

* **model:** define Tetromino class, shapes and tests ([720ae37](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/720ae378a813614482af4aaa93e39a1e136ebaf2))

## [0.1.3](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/compare/v0.1.2...v0.1.3) (2026-02-02)


### Bug Fixes

* **deploy:** update new_release variable to publish to PyPI ([4e826a5](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/4e826a55c2080d16ab1ae6ebce6119c571b8e1b8))

## [0.1.2](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/compare/v0.1.1...v0.1.2) (2026-02-02)


### Bug Fixes

* guess that everything's ready, ci/cd included ([776e1cc](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/776e1cc12373bb57f231ce40a3ed0776e73f7147))

# 0.1.1 (2026-02-02)


### Bug Fixes

* could not find observer ([17e46c9](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/17e46c988970105b7588b9ec21002b2bbf8c030e))
* define first modules of model and gui ([c93b6a5](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/c93b6a598c5173acbb9e1f8eca85dd3dc018779f))
* move scripts in tasks ([806975f](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/806975f96c2f338af17ba0efc620358fec49903c))
* typify classes and methods ([fda4d99](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/fda4d9989697dc67a63a1743ac2cc6e65b7f727d))
* update build and release ([fef5cd9](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/fef5cd976732f409ad622ef4772da597c16e792b))
* update pre-commit operations ([cae804b](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/cae804bbfb523cc90d454f22b8aa571b5979a037))
