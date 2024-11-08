## 0.3.2 (2024-11-08)

### Fixes

- **ticks**: fix to log array ticks not all displaying [slaclau](seb.laclau@gmail.com) (d173b3736863f99de6b1520ab12f970bc2b24da9)

## 0.3.1 (2024-11-07)

### Documentation

- **README**: update [slaclau](seb.laclau@gmail.com) (86ffaff03fdbdcccce9d2145f739985ada370a98)

## 0.3.0 (2024-11-07)

### Features

- **demo**: add demo for plotly shift axes by a number of pixels (#14) [slaclau](seb.laclau@gmail.com) (53e0c369cf5c3701b18d52d6134f6dceacc3624e)
- implement functionality required for plotly autoshift (#14) [slaclau](seb.laclau@gmail.com) (04b4afa9961253d25b437a039cfa55ea4ade2e73)
- implement functionality required for plotly multiple axes (#14) [slaclau](seb.laclau@gmail.com) (6242b83b97b21c89167418b4c38af2051d1bd419)
- implement functionality required for plotly multiple y axes subplots demo (#14) [slaclau](seb.laclau@gmail.com) (df1e20575ed9d9bad0524baeca77352ae91c27de)
- implement functionality required for plotly two y axis demo (#14) [slaclau](seb.laclau@gmail.com) (4851e86bbb03301e6fe7cf62a601b29e44da3fa6)
- **ticks**: SI format for ticks [slaclau](seb.laclau@gmail.com) (6534107fbeb991484c42417d547abf06f5c15122)

### Fixes

- **chart**: correctly update domain for overlaying axes on off side [slaclau](seb.laclau@gmail.com) (f00c64d6f9bae8b761c0a03af6a57480430799b0)
- **chart**: fix axis ordering when no y axes on one side [slaclau](seb.laclau@gmail.com) (f5f7796b5b19a8ae4ed34cc3cdb96605200f5d19)
- **ticks**: change si prefix thresholds to better match plotly [slaclau](seb.laclau@gmail.com) (371c9ba8b439e692f06eca9e577aef0172f138bb)
- **chart**: don't change axis range on hide if only one trace on axis [slaclau](seb.laclau@gmail.com) (6a3c2be917850c2183e4c7d54c48eaf4d09ac19a)

### Build

- **pyproject.toml**: add prefixed to deps [slaclau](seb.laclau@gmail.com) (ad46ba7efa43b40daaaafc5420a69113a793ca04)

## 0.2.6 (2024-11-05)

## 0.2.5 (2024-11-05)

## 0.2.4 (2024-11-05)

## 0.2.3 (2024-11-05)

## 0.2.2 (2024-11-05)

## 0.2.1 (2024-11-04)

### Fixes

- **chart.py**: fix detecting axis type for default axes - i.e. when xaxis or yaxis is not defined (#12) [slaclau](77557628+slaclau@users.noreply.github.com) (af9083dfd3eaa55274917bbf380e2bbf5eae9acf)

## 0.2.0 (2024-09-15)

### Features

- introduce log axes (#3) [slaclau](77557628+slaclau@users.noreply.github.com) (538793375711538c77f1974ae917ef1e8226c907)
- load plotly template from json [slaclau](seb.laclau@gmail.com) (ed512148d544d83e4de6fc6326eec12f58813539)
- make plotly.go optional [slaclau](seb.laclau@gmail.com) (05e444460b827820939d380898bba09de8bf5441)
- commit plotly schema [slaclau](seb.laclau@gmail.com) (3e302d8d45e22ae6a005691dd8664263d830eaa2)
- add plotly_types [slaclau](seb.laclau@gmail.com) (5be0672a1d7bf78010dd77708aad0477e68d352b)

### Fixes

- **lint.yaml**: fix issue with pygobject installation [slaclau](seb.laclau@gmail.com) (d2875ef42b6a4359957f4e33e0bbb0d54f756624)
- reviewdog permissions (#8) [slaclau](77557628+slaclau@users.noreply.github.com) (f68a8e47dded56ff81008114149c181172d0c0a9)
- update ticks when trace visibility is changed [slaclau](seb.laclau@gmail.com) (44244c37c981d738506f4465edd258559255be24)
- fix legend when legendgroup is blank [slaclau](seb.laclau@gmail.com) (9ce6a29b028084eaf7d874dd183ba76995a3c27c)
- fix grid lines and background for log axes [slaclau](seb.laclau@gmail.com) (f5cb4a612fe936b87b8cc36a78534b51a6223027)
- pass additional demos from https://plotly.com/python/line-and-scatter/ [slaclau](seb.laclau@gmail.com) (26530a236cecde784226b9460d12ed1b751aafab)
- pass 4 demos from https://plotly.com/python/line-and-scatter/ [slaclau](seb.laclau@gmail.com) (dd4d4b59a35a267508c8e521c4a3a8471a448a4f)

### Documentation

- add badges to README.md (#2) [slaclau](seb.laclau@gmail.com) (591fc67925b2bd2b3a209621d6c47246000fb44f)
- tidy sphinx config (#2) [slaclau](seb.laclau@gmail.com) (cbc4a78652287017910787c12e1f1664e891e92c)
- update README.md [slaclau](77557628+slaclau@users.noreply.github.com) (81a4e0c28f3ae0826c7adc2862b9bd73ddd705dc)
- include figures from demo/broadway/test_broadway.py in sphinx documentation (#1) [slaclau](77557628+slaclau@users.noreply.github.com) (d8c35047ddef3ae13c577ec200b1de6ca9bcccce)
- add RTD config [slaclau](77557628+slaclau@users.noreply.github.com) (74957db33643e319233cec508502bfe2ca769ab6)
- update README.md [slaclau](77557628+slaclau@users.noreply.github.com) (0fcf121bd37b425cd0944c6d73760c0009bb6095)
- sphinx setup [slaclau](seb.laclau@gmail.com) (fd3e35e4094956abeaa6a4928d55c23f3b15ef17)

### Build

- include demo tests in test report [slaclau](seb.laclau@gmail.com) (2c29ac9ddc18ec6025acb3b3b1ccb27eac8a5534)
- **commitizen**: use custom plugin cz-trailers (#5) [slaclau](seb.laclau@gmail.com) (cd18d33d2d94925f45d780f498d8752962cd5232)
- add commitizen [slaclau](77557628+slaclau@users.noreply.github.com) (6e9bf3c499334204bc2b0ed2fb7805feb1d46681)
- add coverage config (#2) [slaclau](seb.laclau@gmail.com) (81f23c981dfc17b2fb4b26a94fd7d2cca9c160b1)
- add linting workflow (#2) [slaclau](seb.laclau@gmail.com) (98574b8d386dc5170796a8e11293692bf6c7f1bb)
- create dependabot.yml [slaclau](77557628+slaclau@users.noreply.github.com) (f5fb58b328bab84ac9aa661ff18fd6ea81e35db1)
- get upstream plotly schema and templates [slaclau](77557628+slaclau@users.noreply.github.com) (d926f6a1d3471a51e04487529980122b89ec65cb)
- update workflows [slaclau](seb.laclau@gmail.com) (481cffe3a68613abe4437625c903bee427615c75)
- add gh-pages workflow [slaclau](seb.laclau@gmail.com) (31461e44b6298f43459034f161bcd9d7d7b6bcc2)
- update deps and pylint config in pyproject.toml [slaclau](seb.laclau@gmail.com) (abf6d6abdc96b61ed2dd81bad7b6b7df8e2e7ca4)

## 0.1.0 (2024-07-11)
