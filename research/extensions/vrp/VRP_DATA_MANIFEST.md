# TSMOM-VRP-01 — DATA MANIFEST (S2A acquisition and hash pinning)

```
LINEAGE                    = TSMOM-VRP-01
CONTRACT                   = VRP_PREREGISTRATION.md §L (data acquisition contract)
S1_SEAL_COMMIT             = 16d84545ba1385a482dbac7e776b31275f6fa5f7
ACQUIRED_UTC               = 2026-09-14T08:22:51Z
RAW_DATA_COMMITTED         = NO  (data/ is git-ignored; this manifest and the hashes are tracked)
LICENSE_STATUS             = Cboe personal / research use; NO REDISTRIBUTION;
                             raw bytes retained in the git-ignored data/vix/ tree
TRANSFORMATION_STATUS      = RAW for every file below; the normalized layer is derived
                             and re-derivable from these bytes alone
CREDENTIALS                = NONE. Both endpoints are public and unauthenticated; no
                             key, token or secret was used, sent, stored, logged or hashed.
```

## 1. Sources and authority

Both endpoints are **Cboe official** (`SOURCE_AUTHORITY_LEVEL = 1 / PRIMARY`). No vendor
copy is used anywhere in this lineage, so §L's fallback-authority clause is never
exercised. The settlement field taken is the official **`Settle`** column — never
`Close`, never last trade, never the Special Opening Quotation.

| # | Endpoint | Pattern | Covers |
|---|---|---|---|
| 1 | Cboe delisted-contract archive | `https://cdn.cboe.com/resources/futures/archive/volume-and-price/CFE_<code><yy>_VX.csv` | the older monthly contracts, whole contract life |
| 2 | Cboe market-statistics historical data | `https://cdn.cboe.com/data/us/futures/market_statistics/historical_data/VX/VX_<final_settlement_date>.csv` | the newer monthly contracts |

**Operative-source rule (mechanical; uses no return and cannot change an estimand).**
Where both endpoints serve one contract, the operative file is the one with the greater
number of rows carrying an official settlement; ties break by greater row count, then by
ARCHIVE. Both files are pinned either way and their comparable settlements are
cross-checked on every common date.

## 2. Coverage summary (mechanical counts only)

```
CONTRACT_COUNT                             = 268
FIRST_AVAILABLE_DATE                       = 2004-03-26
LAST_AVAILABLE_DATE                        = 2026-09-11
EXCHANGE_SESSIONS                          = 5654
CHAIN_DAYS                                 = 5617
NUMBER_OF_ROWS                             = 47160
NUMBER_OF_SETTLED_ROWS                     = 46331
NUMBER_OF_DUPLICATES                       = 0
STAGE_A_FIRST_MONTH                        = 2006-09
STAGE_A_LAST_MONTH                         = 2026-08
STAGE_A_MONTHS                             = 240
MONTHLY_CONTRACT_COUNT_IN_WINDOW           = 242
NUMBER_OF_MISSING_SETTLEMENTS_IN_WINDOW    = 0
NUMBER_OF_CONTRACTS_WITH_GAPS_IN_WINDOW    = 0
SPECIFICATION_BREAK_COUNT                  = 1
TICK_HISTORY_BREAK_COUNT                   = 1
EXPIRY_RULE_BREAK_COUNT                    = 1
EXPIRY_RULE_MATCH_COUNT                    = 264
CALENDAR_MISMATCH_COUNT                    = 0
CALENDAR_DECLARED_CFE_ONLY_SESSIONS        = 3
RAW_CONTRACT_FILES_PINNED                  = 274
SPECIFICATION_DOCUMENTS_PINNED             = 7
TOTAL_RAW_BYTES                            = 3791086
```

### Calendar months with no listed standard monthly VX contract

Established mechanically at acquisition: neither Cboe endpoint serves a file for these
months while serving one for every neighbouring month. These are **listing-history**
facts, not data gaps — §F.3 orders contracts by final-settlement date and never assumes
consecutive calendar months.

```
2004-12, 2005-04, 2005-07, 2005-09
```

The remaining entries below (2004-01 … 2004-04) precede the VX listing date
(2004-03-26) and no contract for them ever existed.

| contract month | rule-derived expiry | archive HTTP | current HTTP |
|---|---|---|---|
| 2004-01 | 2004-01-21 | 403 | 403 |
| 2004-02 | 2004-02-18 | 403 | 403 |
| 2004-03 | 2004-03-17 | 403 | 403 |
| 2004-04 | 2004-04-21 | 403 | 403 |
| 2004-12 | 2004-12-22 | 403 | 403 |
| 2005-04 | 2005-04-20 | 403 | 403 |
| 2005-07 | 2005-07-20 | 403 | 403 |
| 2005-09 | 2005-09-21 | 403 | 403 |

## 3. Specification / calendar / fee documents — pinned

| file | SHA256 | bytes | source URL | documents |
|---|---|---|---|---|
| `cboe_vx_contract_specifications.html` | `e3ba2806648a42a88e62b53820fd49659a676f5e02268a5bcd42622923bd7e8e` | 462411 | https://www.cboe.com/tradable_products/vix/vix_futures/specifications/ | Cboe VX standard monthly contract specifications: multiplier, tick, final settlement rule |
| `cfe_holiday_calendar.html` | `ba63a133ff135539e69fd377ea99a9589db974b204efe436073735b6988cef4a` | 479491 | https://www.cboe.com/about/hours/us-futures/ | CFE trading hours and holiday calendar |
| `cfe_fee_schedule.html` | `5655cbccda8a4e69a25323f88c7cc719ddf4b1243767e411401e99c8eb320efa` | 635344 | https://www.cboe.com/us/futures/membership/fee_schedule/ | CFE fee schedule (exchange + clearing), for the documented comparison of section G constants |
| `cboe_vx_historical_data_index.html` | `493721e9db9ee216a243eba2887d71ee48d80490e254c8f3d0a2f7e683e87a6d` | 404482 | https://www.cboe.com/us/futures/market_statistics/historical_data/ | Cboe historical data index page; documents the per-contract file layout used above |
| `CFE-IC-2007-003.pdf` | `f4acc63eea3dc2da9b080c3aac5251e9901233dd9004a966460a0fc39bae7071` | 30067 | https://cdn.cboe.com/resources/regulation/circulars/general/CFE-IC-2007-003.pdf | CFE Information Circular IC07-03 (7 Mar 2007): rescaling of VIX futures effective 26 Mar 2007; multiplier $100 -> $1,000; price divided by 10; minimum tick $0.10 -> 0.01 index point; dollar value per tick unchanged. PRIMARY source for the section F.5 quotation/multiplier break. |
| `datashop_vx_note.html` | `612c409461d959a8743a46c4c4a815284b6c8d54c457dfd55afd1923f38fc3bf` | 51221 | https://datashop.cboe.com/cfe-vix-volatility-index-futures-trades-quotes | Cboe DataShop VX product note: 'Prior to 3/23/2007, VIX had a $100x multiplier. On 3/26/2007 we changed this multiplier to $1000x and divided the display price by 10.' Corroborates IC07-03. |
| `Mini-VIX-Futures-Product-Launch.pdf` | `c74af12fea809c419b415cd32f4a3c95c77efa3572968991c0143478f49e3562` | 164019 | https://cdn.cboe.com/resources/release_notes/2020/Mini-VIX-Futures-Product-Launch.pdf | Cboe Mini VIX (VXM) futures product launch release note; $100 multiplier, used ONLY by the section D.4 integer-granularity check. |

## 4. Raw contract files — pinned

Every row: FILE NAME · RAW SHA256 · BYTE SIZE · ACQUISITION_TIMESTAMP_UTC · ENDPOINT ·
CONTRACT MONTH · rule-derived final settlement. `TRANSFORMATION_STATUS = RAW` throughout;
raw bytes are never edited in place and a re-fetch that differs from the pinned hash
fails the acquisition loudly.

| contract month | expiry | endpoint | file | SHA256 | bytes | acquired (UTC) |
|---|---|---|---|---|---|---|
| 2004-05 | 2004-05-19 | ARCHIVE | `VX_archive_K04.csv` | `79d4cb49b83609ad2c4ed3a52485597d865a00ebcda39365137576e1849d4175` | 2510 | 2026-09-14T08:16:14Z |
| 2004-06 | 2004-06-16 | ARCHIVE | `VX_archive_M04.csv` | `8f7d49679ff363c23199bcb547143819046645ef5b500e0c2ab0cc3deb80b62b` | 3647 | 2026-09-14T08:16:15Z |
| 2004-07 | 2004-07-21 | ARCHIVE | `VX_archive_N04.csv` | `0d3c1c3aba210f32f453e7af05c07b52b87a1692245ba72cd940f4b8775c8e92` | 2319 | 2026-09-14T08:16:17Z |
| 2004-08 | 2004-08-18 | ARCHIVE | `VX_archive_Q04.csv` | `174aa26f2a3e0ea7832b8fad477b1b40858e2792e0d36a3946e819e4d6c23b48` | 6332 | 2026-09-14T08:16:18Z |
| 2004-09 | 2004-09-15 | ARCHIVE | `VX_archive_U04.csv` | `499c6eaf510706f80f14f160cc646d9233fbec102048ce0f11988435735553b2` | 2761 | 2026-09-14T08:16:20Z |
| 2004-10 | 2004-10-20 | ARCHIVE | `VX_archive_V04.csv` | `1f93a919cf698373cf7965ac828504fe793dedfcf5ca6a5690a4c6e82518ed9e` | 2485 | 2026-09-14T08:16:21Z |
| 2004-11 | 2004-11-17 | ARCHIVE | `VX_archive_X04.csv` | `ffcbdf18b58007dd3e535b551fd38b9b46a94ca9be1c916c52d5a7f6f69d6e25` | 10360 | 2026-09-14T08:16:23Z |
| 2005-01 | 2005-01-19 | ARCHIVE | `VX_archive_F05.csv` | `2709f12bc28cf1902220f8536a2320bb4e5367f3bb93986fba3582998d4b2ca1` | 4069 | 2026-09-14T08:16:26Z |
| 2005-02 | 2005-02-16 | ARCHIVE | `VX_archive_G05.csv` | `3d9efe0b2ee8a12473defe1c4ab0b84bcf09756a9a24250a207905f602396903` | 10743 | 2026-09-14T08:16:28Z |
| 2005-03 | 2005-03-16 | ARCHIVE | `VX_archive_H05.csv` | `62594968fa094735479de320de9428d27349dea3184de9f39959a0329d354f33` | 2805 | 2026-09-14T08:16:29Z |
| 2005-05 | 2005-05-18 | ARCHIVE | `VX_archive_K05.csv` | `a13c37b5c5ab86318a4557f0b40fcc96cb3cc736208c3c3077977fb5a603ec68` | 10630 | 2026-09-14T08:16:32Z |
| 2005-06 | 2005-06-15 | ARCHIVE | `VX_archive_M05.csv` | `ed880b903014fc7283469740b8d78126b5335962a94ad3048486d1afce1046c7` | 4383 | 2026-09-14T08:16:33Z |
| 2005-08 | 2005-08-17 | ARCHIVE | `VX_archive_Q05.csv` | `550ea3591a0ed4624186473bfff01032eb0c41536e8db1a2211bde6b1baa6c09` | 12677 | 2026-09-14T08:16:35Z |
| 2005-10 | 2005-10-19 | ARCHIVE | `VX_archive_V05.csv` | `57ba8b11e268a7246834dd7b66939590e07c7908cec25a808ba3595268e1557e` | 6317 | 2026-09-14T08:16:38Z |
| 2005-11 | 2005-11-16 | ARCHIVE | `VX_archive_X05.csv` | `4651aff66195325383d5091574ab1dce02b7e5dc8df554183463ac3c6feff9ed` | 13829 | 2026-09-14T08:16:40Z |
| 2005-12 | 2005-12-21 | ARCHIVE | `VX_archive_Z05.csv` | `91aeab19a89172d09d9778a6cc6bcfbd27aee00108866ddc6d639e5c4574be66` | 3198 | 2026-09-14T08:16:41Z |
| 2006-01 | 2006-01-18 | ARCHIVE | `VX_archive_F06.csv` | `d9a42b27df146c1ac496ae0006aa472a2e4246cf0bbda528e617a25c03446a72` | 2917 | 2026-09-14T08:16:43Z |
| 2006-02 | 2006-02-15 | ARCHIVE | `VX_archive_G06.csv` | `9cc20d32136ab971e1a9c7c0388c63ac228d04e31487ff7fcb7cf324ebae11f5` | 13579 | 2026-09-14T08:16:44Z |
| 2006-03 | 2006-03-22 | ARCHIVE | `VX_archive_H06.csv` | `7b0d713748def616003cab70979a312759334de13e2665948335f6cc69c42316` | 3185 | 2026-09-14T08:16:46Z |
| 2006-04 | 2006-04-19 | ARCHIVE | `VX_archive_J06.csv` | `43b2a125da5c50718f1a93b1801d39bd1698908001a5c48257d4526b07ae339c` | 3094 | 2026-09-14T08:16:48Z |
| 2006-05 | 2006-05-17 | ARCHIVE | `VX_archive_K06.csv` | `a1af70546771e3499892f06a5c0c58b1ca8b53047f64f6662430b1bd52d194b9` | 13749 | 2026-09-14T08:16:49Z |
| 2006-06 | 2006-06-21 | ARCHIVE | `VX_archive_M06.csv` | `8180741ba76e256a13de88ba1a1effb072833dc60773a05815fec656343a8da8` | 3237 | 2026-09-14T08:16:51Z |
| 2006-07 | 2006-07-19 | ARCHIVE | `VX_archive_N06.csv` | `8d32e252587a6ae0fb3742de3f4d69ba0b7f8727b776dbcced68b204ce3f3d3b` | 3156 | 2026-09-14T08:16:52Z |
| 2006-08 | 2006-08-16 | ARCHIVE | `VX_archive_Q06.csv` | `37e6e8f08c5b17b9715c7ac6d3bb4e5e2ca45ce0bcae522cb1513af96cc92535` | 12287 | 2026-09-14T08:16:54Z |
| 2006-09 | 2006-09-20 | ARCHIVE | `VX_archive_U06.csv` | `dbb7f27bf488693a0e47b0be1f6d98ce7ac01416cc7b835f3261d13a08b0c7e2` | 3178 | 2026-09-14T08:16:56Z |
| 2006-10 | 2006-10-18 | ARCHIVE | `VX_archive_V06.csv` | `34e02bf21ade9ba48465f95252f08630210dd41af33e6cc25c2e764a82b2df9b` | 3288 | 2026-09-14T08:16:57Z |
| 2006-11 | 2006-11-15 | ARCHIVE | `VX_archive_X06.csv` | `33324f00c80dc704a770a24e0ef1bca05089aabb671eceaa3d375bead4dcb7bb` | 13241 | 2026-09-14T08:16:58Z |
| 2006-12 | 2006-12-20 | ARCHIVE | `VX_archive_Z06.csv` | `c2a994439662e9e77de4cb70766dfe465dc284a54fe8a863de72c3ca7a6589a4` | 4860 | 2026-09-14T08:17:00Z |
| 2007-01 | 2007-01-17 | ARCHIVE | `VX_archive_F07.csv` | `b8990377e95d2a06e6d39d66a89ee5afe043c65f063f37c610c5e1191562d4a8` | 4380 | 2026-09-14T08:17:01Z |
| 2007-02 | 2007-02-14 | ARCHIVE | `VX_archive_G07.csv` | `f9dea23d8b5493853054a3a34859d0a3f3ca1f0fa72dbb84f5cef0c3902629a3` | 17461 | 2026-09-14T08:17:02Z |
| 2007-03 | 2007-03-21 | ARCHIVE | `VX_archive_H07.csv` | `c07b9f8bec01acc19e6500f5d767b7c74eee9eb1a53bf95c9e5ce019d5582d07` | 7579 | 2026-09-14T08:17:03Z |
| 2007-04 | 2007-04-18 | ARCHIVE | `VX_archive_J07.csv` | `da3290835aa00ea2eebcc7d09c7a8a32fd67ebe1c55307a19437ec610ee822b1` | 8688 | 2026-09-14T08:17:05Z |
| 2007-05 | 2007-05-16 | ARCHIVE | `VX_archive_K07.csv` | `27f4589669b502f2702205ca1006e7ea64783ea663d833ec41026ab35b3f96c8` | 21050 | 2026-09-14T08:17:06Z |
| 2007-06 | 2007-06-20 | ARCHIVE | `VX_archive_M07.csv` | `3dc09d27c27385bb5d1f2d7b6b02f1fa9cec62ae75af8eb6fd60dc3318cc8f92` | 8527 | 2026-09-14T08:17:07Z |
| 2007-07 | 2007-07-18 | ARCHIVE | `VX_archive_N07.csv` | `17d2006d64f9e3297be53af089ff3139fe88142d957f0beaab6199a10bec5408` | 8689 | 2026-09-14T08:17:08Z |
| 2007-08 | 2007-08-22 | ARCHIVE | `VX_archive_Q07.csv` | `dd90b5bc10d7d306f4b760c159c7034bf2646b769623599370fee8258639a8c0` | 20701 | 2026-09-14T08:17:10Z |
| 2007-09 | 2007-09-19 | ARCHIVE | `VX_archive_U07.csv` | `796606d6a3224207528118969e09dcef4a5a63dc14b1f891390f96f050de8388` | 8587 | 2026-09-14T08:17:11Z |
| 2007-10 | 2007-10-17 | ARCHIVE | `VX_archive_V07.csv` | `5120052404deb80c26f7a824634bed9fb817386137e360c597de78a83a553617` | 8741 | 2026-09-14T08:17:13Z |
| 2007-11 | 2007-11-21 | ARCHIVE | `VX_archive_X07.csv` | `1b9222b1cbb3ccebfc7b8a024feffd2ca6bdba27a3d88c443a5548f24e8696da` | 17888 | 2026-09-14T08:17:15Z |
| 2007-12 | 2007-12-19 | ARCHIVE | `VX_archive_Z07.csv` | `ef15321abe899c2f4281e64598c212285149df69b41114493aeb50c09bbe66dc` | 10517 | 2026-09-14T08:17:16Z |
| 2008-01 | 2008-01-16 | ARCHIVE | `VX_archive_F08.csv` | `bddc41f083e22e4fddf68b098cf7bc65088d715224f1fcb02c4e3c37e635f73e` | 8731 | 2026-09-14T08:17:17Z |
| 2008-02 | 2008-02-19 | ARCHIVE | `VX_archive_G08.csv` | `c6dcbe7ea07eeb067ff49fea4ab6cadebed2d0ae593a0624533e71d8286eb968` | 17379 | 2026-09-14T08:17:19Z |
| 2008-03 | 2008-03-19 | ARCHIVE | `VX_archive_H08.csv` | `c149234c8966cde8d2508c3fb18e4650d31515842dfc42cef01d2ca39fb66424` | 8657 | 2026-09-14T08:17:20Z |
| 2008-04 | 2008-04-16 | ARCHIVE | `VX_archive_J08.csv` | `685dd9e26d401dce60e89fff2d5a492d2350aebe9cdcf682adfd30c94c241ab2` | 8580 | 2026-09-14T08:17:22Z |
| 2008-05 | 2008-05-21 | ARCHIVE | `VX_archive_K08.csv` | `b6c2b3898a9d2478f86049d3586a02872ab86a46f12bb558fa9ef9322592f530` | 35432 | 2026-09-14T08:17:23Z |
| 2008-06 | 2008-06-18 | ARCHIVE | `VX_archive_M08.csv` | `eeda196f29ed40c969e485e750b618dcf21cfe9853e73982f040fc56b4dd2f3f` | 17338 | 2026-09-14T08:17:24Z |
| 2008-07 | 2008-07-16 | ARCHIVE | `VX_archive_N08.csv` | `98eeee0a95fbcedb708c28264c38a36011b109fa55401270644853416a9055c7` | 9815 | 2026-09-14T08:17:26Z |
| 2008-08 | 2008-08-20 | ARCHIVE | `VX_archive_Q08.csv` | `1db08f6847296ba78600976199c22abd5b67681ced2909ff8641aad9e59367a1` | 17384 | 2026-09-14T08:17:27Z |
| 2008-09 | 2008-09-17 | ARCHIVE | `VX_archive_U08.csv` | `e93965c073e91c7d7c668dae704df98b71ccc44038f34ce6e8750655d85f3056` | 8780 | 2026-09-14T08:17:29Z |
| 2008-10 | 2008-10-22 | ARCHIVE | `VX_archive_V08.csv` | `5f493125bbc9d7a345f7bc4dc67c58aa791aba3eb9775945bf5b25562485d65c` | 9148 | 2026-09-14T08:17:30Z |
| 2008-11 | 2008-11-19 | ARCHIVE | `VX_archive_X08.csv` | `c5a2b0b221025b1d336dcbe143b1c4aa71922ae8225676a7b1354739a407fefa` | 17442 | 2026-09-14T08:17:32Z |
| 2008-12 | 2008-12-17 | ARCHIVE | `VX_archive_Z08.csv` | `3319142be531c9b289c7f18e958d52ec3d09d42ac54a7525dc12656c2509afc2` | 15923 | 2026-09-14T08:17:34Z |
| 2009-01 | 2009-01-21 | ARCHIVE | `VX_archive_F09.csv` | `b9ae1a33dc45315e6731efa46e5e3b137440af538cc87723c97604a4f4be2741` | 13043 | 2026-09-14T08:17:35Z |
| 2009-02 | 2009-02-18 | ARCHIVE | `VX_archive_G09.csv` | `c11ab65a98969952f03145f672c9d2f90fdb8ebc23e7befe6ec7f97bace802fd` | 16897 | 2026-09-14T08:17:37Z |
| 2009-03 | 2009-03-18 | ARCHIVE | `VX_archive_H09.csv` | `124c8f3fa26c1aa50bd88b176103aaf426c726a928ba2dbad3fd637dcbcaf89d` | 13921 | 2026-09-14T08:17:38Z |
| 2009-04 | 2009-04-15 | ARCHIVE | `VX_archive_J09.csv` | `b22a453d4ad58269931210ef5375835d33ceb01ccacb1ef69ccc2cb9e65fdf0a` | 13667 | 2026-09-14T08:17:40Z |
| 2009-05 | 2009-05-20 | ARCHIVE | `VX_archive_K09.csv` | `578c32bb3e60b60f6ec380e8675525bfa9384da725d1a5515314e82140c51d4b` | 13846 | 2026-09-14T08:17:42Z |
| 2009-06 | 2009-06-17 | ARCHIVE | `VX_archive_M09.csv` | `4cba3c482f2dab9bf800fd0ab9e1e69d29c2afec2df3635d6ff406d38c607735` | 13584 | 2026-09-14T08:17:43Z |
| 2009-07 | 2009-07-22 | ARCHIVE | `VX_archive_N09.csv` | `ef71fb9142e23c3d8ee1ffe8429e6f0ffab5f2503f195ed6a3f98afaef4b21dd` | 14406 | 2026-09-14T08:17:45Z |
| 2009-08 | 2009-08-19 | ARCHIVE | `VX_archive_Q09.csv` | `7819182326171e9e5ae51ddfb24a0e6b8e2edb28b59a46caf7b94a3214694a34` | 12388 | 2026-09-14T08:17:46Z |
| 2009-09 | 2009-09-16 | ARCHIVE | `VX_archive_U09.csv` | `6e0986aada1b5279aa36711d89952abecc28a1c9e7b479ef68fed805496f4db9` | 13989 | 2026-09-14T08:17:48Z |
| 2009-10 | 2009-10-21 | ARCHIVE | `VX_archive_V09.csv` | `fd362e2daad15249bcac969186ffba3063646fd43f4300153adb34767ef7da81` | 14767 | 2026-09-14T08:17:49Z |
| 2009-11 | 2009-11-18 | ARCHIVE | `VX_archive_X09.csv` | `827e8717ebc4dfcac9761a1bbbb44ad1b19b7a1199388de626862b4638042db1` | 14921 | 2026-09-14T08:17:51Z |
| 2009-12 | 2009-12-16 | ARCHIVE | `VX_archive_Z09.csv` | `827f55ac4391f64190f1839da4b54fa8aa4719810b708c35c299c1df63f04e9d` | 10634 | 2026-09-14T08:17:52Z |
| 2010-01 | 2010-01-20 | ARCHIVE | `VX_archive_F10.csv` | `3ae116ddaa6a6e769dfa95f13697b601c18d1919e066bf384085158db14c1dcc` | 10831 | 2026-09-14T08:17:54Z |
| 2010-02 | 2010-02-17 | ARCHIVE | `VX_archive_G10.csv` | `90c362ba139cb13419ae9d48c73fa1564c54e1f514737fd1c75d741f30cfbef2` | 10970 | 2026-09-14T08:17:55Z |
| 2010-03 | 2010-03-17 | ARCHIVE | `VX_archive_H10.csv` | `a651567fe0d7b97c34355732c18b19005ce074b87989cfdde944f95bf2c68f9e` | 10448 | 2026-09-14T08:17:56Z |
| 2010-04 | 2010-04-21 | ARCHIVE | `VX_archive_J10.csv` | `bbccd1d89c19cd7ee4d48dfdaea411f7b548ef215fe81434796b4f1e1981c56b` | 10728 | 2026-09-14T08:17:58Z |
| 2010-05 | 2010-05-19 | ARCHIVE | `VX_archive_K10.csv` | `e6149d5b706345972e8873669fee15a2a3381e40be349bc9f2a28c926f820d19` | 11998 | 2026-09-14T08:18:00Z |
| 2010-06 | 2010-06-16 | ARCHIVE | `VX_archive_M10.csv` | `9b64f85a4c38275f29e62ddf1b42dcc56952151a213b2a46680dc26157c417dd` | 11685 | 2026-09-14T08:18:01Z |
| 2010-07 | 2010-07-21 | ARCHIVE | `VX_archive_N10.csv` | `763cc0ba681b934a9fc3c4b8cce4ff076a469d3430ee5979b33ebb8be1fe57a0` | 12062 | 2026-09-14T08:18:02Z |
| 2010-08 | 2010-08-18 | ARCHIVE | `VX_archive_Q10.csv` | `5355342658c4186629e873b51ca6e051960ad07c06902a0c5a30d832a0696931` | 12091 | 2026-09-14T08:18:04Z |
| 2010-09 | 2010-09-15 | ARCHIVE | `VX_archive_U10.csv` | `aeba02ee44fbc5a9c16046c5979a68cd04439a56a40b154a75481e14a3ccc7c1` | 11924 | 2026-09-14T08:18:05Z |
| 2010-10 | 2010-10-20 | ARCHIVE | `VX_archive_V10.csv` | `5549a86a572f7c5d572fbd07b05744288d2485d365ff19731f06cd6fe2ffa911` | 12299 | 2026-09-14T08:18:07Z |
| 2010-11 | 2010-11-17 | ARCHIVE | `VX_archive_X10.csv` | `b6584d30fa0b3da062698c1ee92c175719f1d12962958b1582e653f998bcfb80` | 12351 | 2026-09-14T08:18:09Z |
| 2010-12 | 2010-12-22 | ARCHIVE | `VX_archive_Z10.csv` | `de5b2291a942f77245aa68745a494b768108182a47edd2b0ba9390f80c25d4d2` | 12470 | 2026-09-14T08:18:10Z |
| 2011-01 | 2011-01-19 | ARCHIVE | `VX_archive_F11.csv` | `ad8e031d725ec296e5d7b72dbbb23be8d8f9ac4d5df0c38db792bfa796b4c71e` | 12285 | 2026-09-14T08:18:11Z |
| 2011-02 | 2011-02-16 | ARCHIVE | `VX_archive_G11.csv` | `2623402e9c7b0009c507a44f1f65c1a275b5818692446263f4e9d244f76adb7e` | 12378 | 2026-09-14T08:18:13Z |
| 2011-03 | 2011-03-16 | ARCHIVE | `VX_archive_H11.csv` | `fff753ba3b24941e03ea7f006534b6ca4551ba9b2cfd441a6ba2707d6145074a` | 12139 | 2026-09-14T08:18:15Z |
| 2011-04 | 2011-04-20 | ARCHIVE | `VX_archive_J11.csv` | `45a8a5c1cc0f824e1213f205ab2a954a148416ad07fc9dce05e895246ee12207` | 12447 | 2026-09-14T08:18:16Z |
| 2011-05 | 2011-05-18 | ARCHIVE | `VX_archive_K11.csv` | `75fd3c4ddbcba8a2702c2086cf37284682596d94e53e418cbede5fb46b6222a8` | 12237 | 2026-09-14T08:18:18Z |
| 2011-06 | 2011-06-15 | ARCHIVE | `VX_archive_M11.csv` | `4fd04271e39dcd52c33cce7a1d8ad47c725a82f326272590e4749866af422402` | 12008 | 2026-09-14T08:18:20Z |
| 2011-07 | 2011-07-20 | ARCHIVE | `VX_archive_N11.csv` | `47304e8a6b0adf1f6877321b37078d77e27473548ce545924424b78f055fcfc9` | 12424 | 2026-09-14T08:18:20Z |
| 2011-08 | 2011-08-17 | ARCHIVE | `VX_archive_Q11.csv` | `2376d2cd88d72c42660c4bde0ac20404114bbbeeb046901de1f429b8f6b2a0d5` | 12566 | 2026-09-14T08:18:22Z |
| 2011-09 | 2011-09-21 | ARCHIVE | `VX_archive_U11.csv` | `63eff26f1492fd24bab4886ebaff7bb97d805cc872d26802f188c8169e776fd7` | 12755 | 2026-09-14T08:18:24Z |
| 2011-10 | 2011-10-19 | ARCHIVE | `VX_archive_V11.csv` | `a870b7854635baff74d32fe93fab5f5a2b3471a0d5797d45398846ae997eea91` | 12398 | 2026-09-14T08:18:25Z |
| 2011-11 | 2011-11-16 | ARCHIVE | `VX_archive_X11.csv` | `99da1becac78bc27aaa10ca1b63247862e8f5edfdd33da96c5c993cf3a6e4650` | 12475 | 2026-09-14T08:18:27Z |
| 2011-12 | 2011-12-21 | ARCHIVE | `VX_archive_Z11.csv` | `f49786fda02509a3d095167601bf32f792c03449039621102a59ce85a11ac59b` | 12239 | 2026-09-14T08:18:28Z |
| 2012-01 | 2012-01-18 | ARCHIVE | `VX_archive_F12.csv` | `c1a5d120de89335d49c548fa6b733820ee332ab18d12eb85c75014f4de189b5b` | 11990 | 2026-09-14T08:18:29Z |
| 2012-02 | 2012-02-15 | ARCHIVE | `VX_archive_G12.csv` | `8d6eb05cc661d8a34425b0e4e1aa104732782f2cbd507760e129b1316d0fb16d` | 11975 | 2026-09-14T08:18:30Z |
| 2012-03 | 2012-03-21 | ARCHIVE | `VX_archive_H12.csv` | `3112642c83381eef19d2d7072413b051956a61bdad1782cf470453dd802759d1` | 12041 | 2026-09-14T08:18:31Z |
| 2012-04 | 2012-04-18 | ARCHIVE | `VX_archive_J12.csv` | `0c4dc1d3bbe3ba959ed8b9c6ac63958f6eaf1211a56dce4e6d5b861b2e4629e4` | 11960 | 2026-09-14T08:18:33Z |
| 2012-05 | 2012-05-16 | ARCHIVE | `VX_archive_K12.csv` | `c1290ed13d37ad75fbfc205c79beee7c3ccdee8d3dde186fbf34572d977efa0e` | 13304 | 2026-09-14T08:18:34Z |
| 2012-06 | 2012-06-20 | ARCHIVE | `VX_archive_M12.csv` | `2cea0810c7781cc6f8d27b482ce00852644f2fd574bb0ce4a1ce807b9db5fc5d` | 13505 | 2026-09-14T08:18:36Z |
| 2012-07 | 2012-07-18 | ARCHIVE | `VX_archive_N12.csv` | `61809f1cf7a39ee0c327bfdf3ce287a18763fb4685eafe0943bc3bdf480ae9a4` | 13596 | 2026-09-14T08:18:37Z |
| 2012-08 | 2012-08-22 | ARCHIVE | `VX_archive_Q12.csv` | `5583e258859c9f3a98560b2f1b912b22b7f0b969a2ea571547a6efefbd44aac9` | 14124 | 2026-09-14T08:18:39Z |
| 2012-09 | 2012-09-19 | ARCHIVE | `VX_archive_U12.csv` | `d3fa26d2408eaa4a6c3a38a7918aa9438732a6db9893c69c820f96029064ae36` | 13833 | 2026-09-14T08:18:40Z |
| 2012-10 | 2012-10-17 | ARCHIVE | `VX_archive_V12.csv` | `f744c34639f0f347249485ff83f5bb14f6af23095e87c8fbf37a22f8f4636a99` | 14001 | 2026-09-14T08:18:41Z |
| 2012-11 | 2012-11-21 | ARCHIVE | `VX_archive_X12.csv` | `ee4693ad2a9c64738b3e2af52c1e3331c9d3dcb3036ea246f7791d879e5fcfcb` | 14189 | 2026-09-14T08:18:43Z |
| 2012-12 | 2012-12-19 | ARCHIVE | `VX_archive_Z12.csv` | `2298b1f4cfdb95157a7ddc5b3b3fed946f123da7a677b28e7c6002840b1e25a3` | 13708 | 2026-09-14T08:18:44Z |
| 2013-01 | 2013-01-16 | ARCHIVE | `VX_archive_F13.csv` | `5e880a72439277bc6a274c2b4e233da1b6d12ce235d4a7fa2707785675f933d8` | 13813 | 2026-09-14T08:18:45Z |
| 2013-01 | 2013-01-16 | CURRENT | `VX_current_2013-01-16.csv` | `637d9a8c0d6fd8a5a1b6d035e662b440cc61ca7206aba3968587ba37b49154c5` | 933 | 2026-09-14T08:18:45Z |
| 2013-02 | 2013-02-13 | ARCHIVE | `VX_archive_G13.csv` | `6f9444dec4221ae7322cef81566ee769721f82d500cfc1ffd4a6cf1c867c9cca` | 13829 | 2026-09-14T08:18:46Z |
| 2013-02 | 2013-02-13 | CURRENT | `VX_current_2013-02-13.csv` | `7402f4dfe90c93df3e8b88d92ae211a0ce2ab73a58de511adb339e1974b99075` | 2418 | 2026-09-14T08:18:47Z |
| 2013-03 | 2013-03-20 | ARCHIVE | `VX_archive_H13.csv` | `fec608165d22c39f327b5fbf9709e3954fc72bce667c7b700469197be79e61fe` | 13805 | 2026-09-14T08:18:48Z |
| 2013-03 | 2013-03-20 | CURRENT | `VX_current_2013-03-20.csv` | `8ef55a7d2d9246c5ce4e286a53d8b0acc80f250acdf9652640573bef490bcd76` | 4258 | 2026-09-14T08:18:49Z |
| 2013-04 | 2013-04-17 | ARCHIVE | `VX_archive_J13.csv` | `b370081464894229f7da4211528085b4fe1b8ac88d5ebeaf0455985b93553976` | 13747 | 2026-09-14T08:18:49Z |
| 2013-04 | 2013-04-17 | CURRENT | `VX_current_2013-04-17.csv` | `6f45bb6c481121f2a5da6cd423699939d76fc99245489d3a0fdaf4756268f305` | 5683 | 2026-09-14T08:18:50Z |
| 2013-05 | 2013-05-22 | ARCHIVE | `VX_archive_K13.csv` | `4869dedda18bda69213a557360cd7715c74873935612e421a9e2a089689cc79f` | 14198 | 2026-09-14T08:18:51Z |
| 2013-05 | 2013-05-22 | CURRENT | `VX_current_2013-05-22.csv` | `d37b794a921a7ac691370ff6b23a925216bdf8f47e241a51c4f4c17d8dd7fa77` | 7600 | 2026-09-14T08:18:52Z |
| 2013-06 | 2013-06-19 | ARCHIVE | `VX_archive_M13.csv` | `731321cfa8c54f5b9f64e76acf33b2d6bc21a2fed4fef365ea6faa44f3de86f5` | 13674 | 2026-09-14T08:18:53Z |
| 2013-06 | 2013-06-19 | CURRENT | `VX_current_2013-06-19.csv` | `cca2f88a792c21bce6c2a690bd009467660a24900d805ff2e4f0105fe47fa19f` | 9211 | 2026-09-14T08:18:53Z |
| 2013-07 | 2013-07-17 | CURRENT | `VX_current_2013-07-17.csv` | `c812baff00929d2458f5782b27b3ef65265c6a9a6b18924a1f68df4e0e24ab01` | 10821 | 2026-09-14T08:18:54Z |
| 2013-08 | 2013-08-21 | CURRENT | `VX_current_2013-08-21.csv` | `ff18a4b2e59f10e220e2f61f17e388d9453d377d4d327e1554205959a5d416f1` | 12947 | 2026-09-14T08:18:56Z |
| 2013-09 | 2013-09-18 | CURRENT | `VX_current_2013-09-18.csv` | `872a3a5258dd17cf6e81f25df3c415716adf9a2868f8839c8185720ee020e61b` | 14485 | 2026-09-14T08:18:58Z |
| 2013-10 | 2013-10-16 | CURRENT | `VX_current_2013-10-16.csv` | `73374c275e18fcf315ce88c60a5a3d0f51d1131ffeb1ee4e49b909a5339eb25d` | 15186 | 2026-09-14T08:18:59Z |
| 2013-11 | 2013-11-20 | CURRENT | `VX_current_2013-11-20.csv` | `a3f304d0dc58bfaa519b4cd37d9371e39cb9faea4db2d0c91affc9a9947f3848` | 16021 | 2026-09-14T08:19:00Z |
| 2013-12 | 2013-12-18 | CURRENT | `VX_current_2013-12-18.csv` | `7d8f14b22c810a7918ff1c061f3a8ba6a1905efac388814374b9e6e059211cac` | 15809 | 2026-09-14T08:19:02Z |
| 2014-01 | 2014-01-22 | CURRENT | `VX_current_2014-01-22.csv` | `d5d3f8db6146aa08b2bfda7bb2f7b6c435b0f0aa75ef939027d0b3edd64bfbc1` | 16227 | 2026-09-14T08:19:03Z |
| 2014-02 | 2014-02-19 | CURRENT | `VX_current_2014-02-19.csv` | `15032cb7c7f2e71fa0cdc996c68f5b427ed2487d5773cab7547a361fc38d5f97` | 16034 | 2026-09-14T08:19:04Z |
| 2014-03 | 2014-03-18 | CURRENT | `VX_current_2014-03-18.csv` | `71324b5a73ba18d4859ceb33da5f83bb3cf9cdaa82be3cd1ec17ed88aa4ce629` | 15978 | 2026-09-14T08:19:06Z |
| 2014-04 | 2014-04-16 | CURRENT | `VX_current_2014-04-16.csv` | `e186eec5fc46b59f885cfa26b52f2d6b1f920fb81d85becf425468ddc3debdcb` | 16161 | 2026-09-14T08:19:07Z |
| 2014-05 | 2014-05-21 | CURRENT | `VX_current_2014-05-21.csv` | `e7cda391897612ffa3b9dfe043a9fa7037a70975b47e9418adbb9a46bd6bb06c` | 16065 | 2026-09-14T08:19:09Z |
| 2014-06 | 2014-06-18 | CURRENT | `VX_current_2014-06-18.csv` | `67f188b5710a653e22b3c8afd911b25a42bc3ac1be237a38e4de4481e7594549` | 16047 | 2026-09-14T08:19:11Z |
| 2014-07 | 2014-07-16 | CURRENT | `VX_current_2014-07-16.csv` | `d9186d832169a62371cfce07438ea5833503235ad305c83c590ff02f9ceded31` | 15941 | 2026-09-14T08:19:12Z |
| 2014-08 | 2014-08-20 | CURRENT | `VX_current_2014-08-20.csv` | `1cf327407b0df7d95855569d5d7b48929ac49efd9548c131ff1455e903b47bb1` | 15938 | 2026-09-14T08:19:14Z |
| 2014-09 | 2014-09-17 | CURRENT | `VX_current_2014-09-17.csv` | `c7f363c0ba88a335e8d477a997e73f15b12ca34e3aa6ef8a7a5a4da410c42a2a` | 15930 | 2026-09-14T08:19:15Z |
| 2014-10 | 2014-10-22 | CURRENT | `VX_current_2014-10-22.csv` | `ffc837e32032cae60653999f91b06ad27bb7096ceccfc46a891f439eea413a0e` | 16236 | 2026-09-14T08:19:16Z |
| 2014-11 | 2014-11-19 | CURRENT | `VX_current_2014-11-19.csv` | `ff1bebfbe24b1e6bf2f8401d6df61bdc37fda1ba7657806a165257c2d2a39180` | 16360 | 2026-09-14T08:19:18Z |
| 2014-12 | 2014-12-17 | CURRENT | `VX_current_2014-12-17.csv` | `22d871cdfbc45dfeee9695ec46ddc5ca4e3218150634fc9ebb4acabdf9801d2c` | 16259 | 2026-09-14T08:19:20Z |
| 2015-01 | 2015-01-21 | CURRENT | `VX_current_2015-01-21.csv` | `41f91ba132ef95d0d08b406632fc7287d0ae33549638bbae5fe74353f3b50067` | 16453 | 2026-09-14T08:19:21Z |
| 2015-02 | 2015-02-18 | CURRENT | `VX_current_2015-02-18.csv` | `031a8bee01141dee071e95db1736f0123c8d9f61c2e06c0445035db185eee495` | 15942 | 2026-09-14T08:19:22Z |
| 2015-03 | 2015-03-18 | CURRENT | `VX_current_2015-03-18.csv` | `a6f97e10b12cfd879c1909726e36f78f67308a25b64306ab7cb035336da6b728` | 16023 | 2026-09-14T08:19:24Z |
| 2015-04 | 2015-04-15 | CURRENT | `VX_current_2015-04-15.csv` | `0f76e3367e83899aeb630373c03756cfdaa378815c253df1e99f8a1ce32c34ee` | 16116 | 2026-09-14T08:19:25Z |
| 2015-05 | 2015-05-20 | CURRENT | `VX_current_2015-05-20.csv` | `7f9ef8a648e5941633d1d698fe0df5a1028742be6419dd739519d579866a1431` | 16146 | 2026-09-14T08:19:27Z |
| 2015-06 | 2015-06-17 | CURRENT | `VX_current_2015-06-17.csv` | `dfd038349b2bf5b42201098bfd773154dffc00e95fca40a546460895706ae5b3` | 16092 | 2026-09-14T08:19:29Z |
| 2015-07 | 2015-07-22 | CURRENT | `VX_current_2015-07-22.csv` | `716680bec93ae4e2ad275de6205ff465e8a280d75aa794a78760d942163e2e5d` | 16001 | 2026-09-14T08:19:30Z |
| 2015-08 | 2015-08-19 | CURRENT | `VX_current_2015-08-19.csv` | `db84d1d673c2a9f26cb8da329c30128607b1d54fc2b6b22dac662bab5deb140c` | 16010 | 2026-09-14T08:19:31Z |
| 2015-09 | 2015-09-16 | CURRENT | `VX_current_2015-09-16.csv` | `8cd9ed89f3b134dcd079d75836c4b484eb7996220327f96ed3fe7eacbfe86f71` | 15977 | 2026-09-14T08:19:33Z |
| 2015-10 | 2015-10-21 | CURRENT | `VX_current_2015-10-21.csv` | `be9ab48393f87cecf4405260faaa117fb2350a10c27c68788cd2d03c8d0108ab` | 16216 | 2026-09-14T08:19:34Z |
| 2015-11 | 2015-11-18 | CURRENT | `VX_current_2015-11-18.csv` | `c264a160247da17575d26f5f3b1903b7a2844033ea8325e6d3d045eb5e25a913` | 16307 | 2026-09-14T08:19:36Z |
| 2015-12 | 2015-12-16 | CURRENT | `VX_current_2015-12-16.csv` | `781f9d1b72a9b9ba842c57a3462497db7cfe106a638e6f76ac06fe58c388308a` | 16231 | 2026-09-14T08:19:37Z |
| 2016-01 | 2016-01-20 | CURRENT | `VX_current_2016-01-20.csv` | `aeea0930e1c1b5687c7304cd5a2ed03dcaf9e40f76bfee12e39724ca1e66792a` | 16359 | 2026-09-14T08:19:39Z |
| 2016-02 | 2016-02-17 | CURRENT | `VX_current_2016-02-17.csv` | `075420a20cbe4638ecbb816ea1ab30e884ca073dc8c6b18f2eaabf934dcf494b` | 15823 | 2026-09-14T08:19:40Z |
| 2016-03 | 2016-03-16 | CURRENT | `VX_current_2016-03-16.csv` | `3cd20339c7a6fef1c0979e90df62a17cae3158344eb2e89c0d499d86c7260745` | 15926 | 2026-09-14T08:19:41Z |
| 2016-04 | 2016-04-20 | CURRENT | `VX_current_2016-04-20.csv` | `393dc45b85ce059739bbe328da511feb7a5f59ccef23d6da3ac159cd430fdd91` | 15949 | 2026-09-14T08:19:43Z |
| 2016-05 | 2016-05-18 | CURRENT | `VX_current_2016-05-18.csv` | `aba10814ffe052491b3a326afff42ee5c5ac3986a164e192ad1a300e2e419499` | 15942 | 2026-09-14T08:19:44Z |
| 2016-06 | 2016-06-15 | CURRENT | `VX_current_2016-06-15.csv` | `1101fe08a03e5ede056d1566dc44bf2becd64d385620c04701b827edd1f7a71d` | 15852 | 2026-09-14T08:19:45Z |
| 2016-07 | 2016-07-20 | CURRENT | `VX_current_2016-07-20.csv` | `014b65d3ac1144eb04b7dc381b975da9a5507731a529f238724a800502764521` | 15852 | 2026-09-14T08:19:47Z |
| 2016-08 | 2016-08-17 | CURRENT | `VX_current_2016-08-17.csv` | `e81b49d8bf1daf53328e77f4c0aa648f863273445cfccd5b990b5961f7177e43` | 15918 | 2026-09-14T08:19:48Z |
| 2016-09 | 2016-09-21 | CURRENT | `VX_current_2016-09-21.csv` | `f778fc3e4642c0e992e6ad5582db7ca31bc94a43039c999f40556696a2e937df` | 16302 | 2026-09-14T08:19:50Z |
| 2016-10 | 2016-10-19 | CURRENT | `VX_current_2016-10-19.csv` | `707f3ac7b19512d971db6a96936a567eda446e861571317f3dd71d81e3bf688e` | 16123 | 2026-09-14T08:19:52Z |
| 2016-11 | 2016-11-16 | CURRENT | `VX_current_2016-11-16.csv` | `82b88e73cfa95aff4dac5c9b3b8fc7515f1006756a6d4baf68c69313a7e1663d` | 16198 | 2026-09-14T08:19:53Z |
| 2016-12 | 2016-12-21 | CURRENT | `VX_current_2016-12-21.csv` | `59548c21843d208954c670faa8e7332bf98c7ecff9131ef99faa97844eb17c12` | 16599 | 2026-09-14T08:19:54Z |
| 2017-01 | 2017-01-18 | CURRENT | `VX_current_2017-01-18.csv` | `8cc56e11f937e065cd0670708fbcf4b8f7bed30fe91362dddb64b62b38ca5063` | 15971 | 2026-09-14T08:19:55Z |
| 2017-02 | 2017-02-15 | CURRENT | `VX_current_2017-02-15.csv` | `4d23113158ebc3b0445b1d7bc1f6f4c2cb98a7ddff800a541b20e4a105422d84` | 15917 | 2026-09-14T08:19:57Z |
| 2017-03 | 2017-03-22 | CURRENT | `VX_current_2017-03-22.csv` | `dad65fc550fdb332ec587126650a8035cc267985a6f56ce69931ce4bcbabd977` | 16321 | 2026-09-14T08:19:58Z |
| 2017-04 | 2017-04-19 | CURRENT | `VX_current_2017-04-19.csv` | `1bbf0643c00b792e053e5a848568f986ad90b77fa4c0cbb6e9c0d563a330505d` | 15946 | 2026-09-14T08:20:00Z |
| 2017-05 | 2017-05-17 | CURRENT | `VX_current_2017-05-17.csv` | `2566cf9cd35d406e35f88b6d90ac8b22ee673b0024d8bf0baf5f99caadadfe78` | 15956 | 2026-09-14T08:20:02Z |
| 2017-06 | 2017-06-21 | CURRENT | `VX_current_2017-06-21.csv` | `a510e1faecbcecb1017a6afd7abeffc1703a65d3f8aeeb87749e24c82b677201` | 15971 | 2026-09-14T08:20:03Z |
| 2017-07 | 2017-07-19 | CURRENT | `VX_current_2017-07-19.csv` | `b7905ad2d1385b3b0eca354af5a155cc0f3812280f32e343438b65477eab720e` | 15897 | 2026-09-14T08:20:05Z |
| 2017-08 | 2017-08-16 | CURRENT | `VX_current_2017-08-16.csv` | `1517565a43fc34cff1e4ec865f8859a9b4711c9e2a22bc47d0c0b74aa72b2db1` | 15933 | 2026-09-14T08:20:06Z |
| 2017-09 | 2017-09-20 | CURRENT | `VX_current_2017-09-20.csv` | `75713d9de1021f98b522c38a89acead6346f895df5d0c7c4c8459621e72ac05e` | 15957 | 2026-09-14T08:20:07Z |
| 2017-10 | 2017-10-18 | CURRENT | `VX_current_2017-10-18.csv` | `e221c859ae483d88a9bac23e8b9f3fb1dc229489388d566c2e2476e241bd6dbb` | 16164 | 2026-09-14T08:20:09Z |
| 2017-11 | 2017-11-15 | CURRENT | `VX_current_2017-11-15.csv` | `77b6e9e2906739392ba361f1d1c6e9cf8e0b478f647e5ea88d1d0a1fababc22b` | 16146 | 2026-09-14T08:20:11Z |
| 2017-12 | 2017-12-20 | CURRENT | `VX_current_2017-12-20.csv` | `6ef323577e4ae0cb605abbf681b38d52b35648284c0c51435554ca1c3c6859cb` | 16239 | 2026-09-14T08:20:12Z |
| 2018-01 | 2018-01-17 | CURRENT | `VX_current_2018-01-17.csv` | `7825a246b640f7f5e541e4c1d507fc6b21bae78f544718afb70eda7320db2286` | 16031 | 2026-09-14T08:20:14Z |
| 2018-02 | 2018-02-14 | CURRENT | `VX_current_2018-02-14.csv` | `a5b46f776331c120318c8a97304b51f72102531ad751d02d73a64ba613f9ec3e` | 16059 | 2026-09-14T08:20:16Z |
| 2018-03 | 2018-03-21 | CURRENT | `VX_current_2018-03-21.csv` | `7c78a94b9f9c7403467f5236093412a798969c4bdc2e72e7ba577942cbf1a38e` | 16117 | 2026-09-14T08:20:17Z |
| 2018-04 | 2018-04-18 | CURRENT | `VX_current_2018-04-18.csv` | `3920a20b460e45826d871e7473cbb8ed4569a05e77cc2521bbbd1c5a2b350d67` | 16016 | 2026-09-14T08:20:19Z |
| 2018-05 | 2018-05-16 | CURRENT | `VX_current_2018-05-16.csv` | `32804f6248e71c6e014729e3979480cc581f6e4b1221f4ce93d867bd4ccf790b` | 16053 | 2026-09-14T08:20:20Z |
| 2018-06 | 2018-06-20 | CURRENT | `VX_current_2018-06-20.csv` | `6c5ca228bdd8bce9d72703720c77b7ca80462b073829a53a890ff768a46114b1` | 16073 | 2026-09-14T08:20:21Z |
| 2018-07 | 2018-07-18 | CURRENT | `VX_current_2018-07-18.csv` | `042fa86dce5f555489e6201bfac79394d94af53b83bff4f2386b63123b7028ea` | 15967 | 2026-09-14T08:20:22Z |
| 2018-08 | 2018-08-22 | CURRENT | `VX_current_2018-08-22.csv` | `35ed1ae5658e1d3574427c4f1f6ba2effb4dd6d9d8c1450a31deba8f982cf27b` | 16404 | 2026-09-14T08:20:23Z |
| 2018-09 | 2018-09-19 | CURRENT | `VX_current_2018-09-19.csv` | `95e63535525b24056476129ce86927156fa43c2f192be7ce3573becb56306c81` | 16000 | 2026-09-14T08:20:25Z |
| 2018-10 | 2018-10-17 | CURRENT | `VX_current_2018-10-17.csv` | `11fa3df6f434e331800fa23abaef7dc4ac9270199433bf93638c945a2a3dda24` | 16227 | 2026-09-14T08:20:25Z |
| 2018-11 | 2018-11-21 | CURRENT | `VX_current_2018-11-21.csv` | `bf6d078b02a7d7b16d4359d43cd0e10f9e5c9d1257c8f03ca67f33a4793ff113` | 16690 | 2026-09-14T08:20:26Z |
| 2018-12 | 2018-12-19 | CURRENT | `VX_current_2018-12-19.csv` | `b95cf1efd7df610ae76a19ff4c816c62e7bd808d147b36d52fc55d06beef7e6b` | 16228 | 2026-09-14T08:20:28Z |
| 2019-01 | 2019-01-16 | CURRENT | `VX_current_2019-01-16.csv` | `02acfe3646e1816cca399ce9bbbb8a1b02c9410ec1277760448f264f1d96ffe1` | 16072 | 2026-09-14T08:20:29Z |
| 2019-02 | 2019-02-13 | CURRENT | `VX_current_2019-02-13.csv` | `9f0b9f1ddcfd30c54db9a74a24d5bcb109133074f4c1ce7b60f9532c783f28da` | 16019 | 2026-09-14T08:20:31Z |
| 2019-03 | 2019-03-19 | CURRENT | `VX_current_2019-03-19.csv` | `2f86c6a1d6eed44390b8134bff68e186d2a1ae34469deaea1e594eb97ebe91a6` | 15966 | 2026-09-14T08:20:31Z |
| 2019-04 | 2019-04-17 | CURRENT | `VX_current_2019-04-17.csv` | `15b9c792ba9b9d37b9f7b6a930dbad9715f1f83789757b8c9134b16362b1febc` | 16193 | 2026-09-14T08:20:33Z |
| 2019-05 | 2019-05-22 | CURRENT | `VX_current_2019-05-22.csv` | `0f364af221b4de67fc0c95105e8edafba1b634f60237b8b07c33b0d769fa364c` | 16103 | 2026-09-14T08:20:34Z |
| 2019-06 | 2019-06-19 | CURRENT | `VX_current_2019-06-19.csv` | `a0a122738217db57d59481294dd3c2206555d508a1f6f2ea88b7a64324b9162b` | 16127 | 2026-09-14T08:20:36Z |
| 2019-07 | 2019-07-17 | CURRENT | `VX_current_2019-07-17.csv` | `ea2adcccd6dded6cac7139a9191b991f74b33a12fa3328bdae628f47f818ecfd` | 15952 | 2026-09-14T08:20:37Z |
| 2019-08 | 2019-08-21 | CURRENT | `VX_current_2019-08-21.csv` | `d8865c5f71d723b1081460b4979384d5ae8edbf5faa4d078dff1db9ab07a3a4f` | 16100 | 2026-09-14T08:20:38Z |
| 2019-09 | 2019-09-18 | CURRENT | `VX_current_2019-09-18.csv` | `8fbdffbd379c70d7c1b754b2ca9ea97d01bb916aea84c6b5f7984379f57cc350` | 15998 | 2026-09-14T08:20:40Z |
| 2019-10 | 2019-10-16 | CURRENT | `VX_current_2019-10-16.csv` | `24ed3fffe793a77e50312c268ccc09fd402b76b3650afcc579b994f1cd0cc9f5` | 16120 | 2026-09-14T08:20:41Z |
| 2019-11 | 2019-11-20 | CURRENT | `VX_current_2019-11-20.csv` | `4f65b9d64aece0ce838779ab8be34af3f6383d4af7d95f2905769e34cced2a38` | 16690 | 2026-09-14T08:20:42Z |
| 2019-12 | 2019-12-18 | CURRENT | `VX_current_2019-12-18.csv` | `426d90a4d696bb9592e022b311be766a6c6ac808c71a68f4e66712b4a6ef6f32` | 16291 | 2026-09-14T08:20:44Z |
| 2020-01 | 2020-01-22 | CURRENT | `VX_current_2020-01-22.csv` | `88dd32dd13b10c67427b6e2d9a3350d2bc663974aed3f89c87b22ab2cd287eb4` | 16432 | 2026-09-14T08:20:45Z |
| 2020-02 | 2020-02-19 | CURRENT | `VX_current_2020-02-19.csv` | `4282f32fadf5e45e889072f373af2077769e0e6ab11b16c5a74dc6dce5c8b749` | 15898 | 2026-09-14T08:20:47Z |
| 2020-03 | 2020-03-18 | CURRENT | `VX_current_2020-03-18.csv` | `b0754a52316241f15d66f41706d3569f20cdfe1703bbd4cd7f87146cf57beb50` | 15992 | 2026-09-14T08:20:48Z |
| 2020-04 | 2020-04-15 | CURRENT | `VX_current_2020-04-15.csv` | `abcfd156b05a0c8b8b75811e5bf17f1cf1dbfdac0d408231bc48d133e57934ca` | 16010 | 2026-09-14T08:20:50Z |
| 2020-05 | 2020-05-20 | CURRENT | `VX_current_2020-05-20.csv` | `0dce9099b417b8af888244d993b2f77fe8cc0cef77c4473b9ca66dc727a80cef` | 16008 | 2026-09-14T08:20:51Z |
| 2020-06 | 2020-06-17 | CURRENT | `VX_current_2020-06-17.csv` | `5d66bb8cbdd182c0fad4e984fa60ffbde7122388dc218fb91bb10a02faa82d1a` | 15951 | 2026-09-14T08:20:53Z |
| 2020-07 | 2020-07-22 | CURRENT | `VX_current_2020-07-22.csv` | `c5f58ca4a7c62f4b205646064e3038d34751e47ab4bb14aaa9e96be59521a407` | 16200 | 2026-09-14T08:20:54Z |
| 2020-08 | 2020-08-19 | CURRENT | `VX_current_2020-08-19.csv` | `7fa02eb5311f0012391223e6aa7d0b1d7ea2a0992e86bf66366dd5408eeef67e` | 15756 | 2026-09-14T08:20:56Z |
| 2020-09 | 2020-09-16 | CURRENT | `VX_current_2020-09-16.csv` | `bb0fd4d378b682148f1999323e35227a71a4b8a18e95deba5980267bf3c65cf4` | 16535 | 2026-09-14T08:20:57Z |
| 2020-10 | 2020-10-21 | CURRENT | `VX_current_2020-10-21.csv` | `f623bf53dbbb3fccc011dcb4f0df19c8726b91ae6b0f9ccfd9ba31e2ca2ee414` | 18645 | 2026-09-14T08:20:59Z |
| 2020-11 | 2020-11-18 | CURRENT | `VX_current_2020-11-18.csv` | `b4e461566167f08151ab6a44268a61c964c1d828c6ea3e41928996e328dcd02c` | 20181 | 2026-09-14T08:21:00Z |
| 2020-12 | 2020-12-16 | CURRENT | `VX_current_2020-12-16.csv` | `bbb2ec67e0c3993a1c78ba6f77123c52709ff1c142604042eb70d048a71a99fd` | 15678 | 2026-09-14T08:21:01Z |
| 2021-01 | 2021-01-20 | CURRENT | `VX_current_2021-01-20.csv` | `53a84f66db60c505ed1ce0eb8deb0e8c8b013b0488fb02c5671edb80db3379a1` | 15810 | 2026-09-14T08:21:03Z |
| 2021-02 | 2021-02-17 | CURRENT | `VX_current_2021-02-17.csv` | `ed9f4381dead986af6f25f11923c40a1f1997a44f916f417bff36c30df4c8b3c` | 15347 | 2026-09-14T08:21:05Z |
| 2021-03 | 2021-03-17 | CURRENT | `VX_current_2021-03-17.csv` | `ee3ba3bd455cad5772198f3f04d3d3e7179779319cf74d22fe90b23f40a21ff7` | 15494 | 2026-09-14T08:21:06Z |
| 2021-04 | 2021-04-21 | CURRENT | `VX_current_2021-04-21.csv` | `0d707904eafaa6ea39c727a5e843eeb6b692577c63b7ae14835227dd90643029` | 15492 | 2026-09-14T08:21:08Z |
| 2021-05 | 2021-05-19 | CURRENT | `VX_current_2021-05-19.csv` | `6ed8f065f27edf49e137829ce247b2e2533e11640ded0f6a79535583772a4b3b` | 15602 | 2026-09-14T08:21:09Z |
| 2021-06 | 2021-06-16 | CURRENT | `VX_current_2021-06-16.csv` | `b87dac062797b9da171f294d5cd2bcfd2d1513d6b7816ddbba2c7737347b658c` | 15551 | 2026-09-14T08:21:11Z |
| 2021-07 | 2021-07-21 | CURRENT | `VX_current_2021-07-21.csv` | `95fd3d2330eedfdbfa0d65b90c0916c309b43b70e54bd43f1ad91a8f2ea008e9` | 15500 | 2026-09-14T08:21:12Z |
| 2021-08 | 2021-08-18 | CURRENT | `VX_current_2021-08-18.csv` | `fc1cda584f8e667ef85470b84edbe42fb877573652becb51ebbd91ff8b900dab` | 15519 | 2026-09-14T08:21:13Z |
| 2021-09 | 2021-09-15 | CURRENT | `VX_current_2021-09-15.csv` | `c73076114fc912535a6f27f2ceb418f7cf32e08e4f536a4e146de8be48ef9526` | 15468 | 2026-09-14T08:21:14Z |
| 2021-10 | 2021-10-20 | CURRENT | `VX_current_2021-10-20.csv` | `88fb7fe945081fb68984cdb45bee72790526b5bcaf543c54cc8d4b5a790a3e92` | 15839 | 2026-09-14T08:21:16Z |
| 2021-11 | 2021-11-17 | CURRENT | `VX_current_2021-11-17.csv` | `a9e3cf02243b17308013f772bb572cea159d084399bbb74eaccf7acc0751e34e` | 15985 | 2026-09-14T08:21:17Z |
| 2021-12 | 2021-12-22 | CURRENT | `VX_current_2021-12-22.csv` | `e929a9ce4fbde81983feb0029503af903a3170ee09c7422ff51669ca75de9f6e` | 16373 | 2026-09-14T08:21:19Z |
| 2022-01 | 2022-01-19 | CURRENT | `VX_current_2022-01-19.csv` | `41737f15dd52ec81ff903457215a0bcd6ba2870b3ef8dd0ca771b91403efff58` | 15805 | 2026-09-14T08:21:20Z |
| 2022-02 | 2022-02-16 | CURRENT | `VX_current_2022-02-16.csv` | `2f43ba33437708a03914d4140b690321059816328b4f24e631ae6f70a89ebc44` | 15814 | 2026-09-14T08:21:22Z |
| 2022-03 | 2022-03-15 | CURRENT | `VX_current_2022-03-15.csv` | `b0df778b923c87d120da4bfd4f85d89a304e2bef0f7d3b40f951183e5a1d80b4` | 15712 | 2026-09-14T08:21:23Z |
| 2022-04 | 2022-04-20 | CURRENT | `VX_current_2022-04-20.csv` | `988293cd474dcb1e7b8d01279826ab426aab4186db8802cc9c8f6bea9febf97e` | 15790 | 2026-09-14T08:21:25Z |
| 2022-05 | 2022-05-18 | CURRENT | `VX_current_2022-05-18.csv` | `af283c8213f8e95b60395ca243e3d8fc42b7854a8bb5b504bd8815bf1086379b` | 15871 | 2026-09-14T08:21:27Z |
| 2022-06 | 2022-06-15 | CURRENT | `VX_current_2022-06-15.csv` | `9eadf959920fdb4317fae7f1f8ecca8265ab950d8f450c188d6e750fa6552b87` | 15844 | 2026-09-14T08:21:28Z |
| 2022-07 | 2022-07-20 | CURRENT | `VX_current_2022-07-20.csv` | `feedfacfa508083eb0820e83f82c5cb354a2eef1d83ec4e18dcef64b53ffffdf` | 15654 | 2026-09-14T08:21:29Z |
| 2022-08 | 2022-08-17 | CURRENT | `VX_current_2022-08-17.csv` | `5000aa4012119373978c50575ce39441a8f8dcad06ab98c340bb2a71dc01053c` | 15727 | 2026-09-14T08:21:31Z |
| 2022-09 | 2022-09-21 | CURRENT | `VX_current_2022-09-21.csv` | `a74598b17c5e92b068ee46ee38aefdfe8423d62153bee7d879ff4eddc2fbb626` | 15819 | 2026-09-14T08:21:32Z |
| 2022-10 | 2022-10-19 | CURRENT | `VX_current_2022-10-19.csv` | `270abe0333366e5395d88d6e56da51fa403962f03229d119a8208ece339c778d` | 15850 | 2026-09-14T08:21:34Z |
| 2022-11 | 2022-11-16 | CURRENT | `VX_current_2022-11-16.csv` | `bb433441c5a2d77f060a86265337d397e56ddfcfa191d2f3dc5f7b474a298379` | 15880 | 2026-09-14T08:21:36Z |
| 2022-12 | 2022-12-21 | CURRENT | `VX_current_2022-12-21.csv` | `4bd0da312422aaa889cbb73bc6643eef556efb2e2599509540fb064657caaf8b` | 16360 | 2026-09-14T08:21:37Z |
| 2023-01 | 2023-01-18 | CURRENT | `VX_current_2023-01-18.csv` | `8c279882f4e81636eae5bf9e99573015ca18edb52384b9b3f6819715cf510561` | 15684 | 2026-09-14T08:21:39Z |
| 2023-02 | 2023-02-15 | CURRENT | `VX_current_2023-02-15.csv` | `9f804c61ba0a51fad872dae5568792a75a2ab21daf5a5972603465898d071d55` | 15700 | 2026-09-14T08:21:40Z |
| 2023-03 | 2023-03-22 | CURRENT | `VX_current_2023-03-22.csv` | `3d35c3f0b0cef53f7808bd7faccf5245869c1972571c58b0727216c646a3571b` | 16045 | 2026-09-14T08:21:41Z |
| 2023-04 | 2023-04-19 | CURRENT | `VX_current_2023-04-19.csv` | `700fc43046fc215e5ae2828cf5983bd4a545f4c2d74be987669da6f666fc49b9` | 15776 | 2026-09-14T08:21:43Z |
| 2023-05 | 2023-05-17 | CURRENT | `VX_current_2023-05-17.csv` | `432cef2e4402d5fc9dc9f0f1540a58099196540987eca39e6ced49eb7fdd10df` | 15773 | 2026-09-14T08:21:44Z |
| 2023-06 | 2023-06-21 | CURRENT | `VX_current_2023-06-21.csv` | `4391c7a0c323e417d2f31685b2a0a0ad6afab79f80689abb128ad54ba8e549ae` | 15699 | 2026-09-14T08:21:46Z |
| 2023-07 | 2023-07-19 | CURRENT | `VX_current_2023-07-19.csv` | `5fbcb598942050a24edba2194a29384b95ee77feb379cfc5e8779463d70785e8` | 15610 | 2026-09-14T08:21:48Z |
| 2023-08 | 2023-08-16 | CURRENT | `VX_current_2023-08-16.csv` | `96e7efc1d13016754a4bd56f53f371f68598c66459409e2293dfe27b8ab02292` | 15686 | 2026-09-14T08:21:49Z |
| 2023-09 | 2023-09-20 | CURRENT | `VX_current_2023-09-20.csv` | `c6b98a1d7be7f1048fdd7db2286de25c54144dd0e6147503156d96602786f55e` | 15697 | 2026-09-14T08:21:50Z |
| 2023-10 | 2023-10-18 | CURRENT | `VX_current_2023-10-18.csv` | `6596d7594ed67016c51191e066c0a8728eda9e8c7ddbdfecf895bb693b859ffa` | 15926 | 2026-09-14T08:21:52Z |
| 2023-11 | 2023-11-15 | CURRENT | `VX_current_2023-11-15.csv` | `3af9d807e0c29efd2d799d34c7be02d2847b4ffd44d27f92d945bc1f711420b2` | 15950 | 2026-09-14T08:21:53Z |
| 2023-12 | 2023-12-20 | CURRENT | `VX_current_2023-12-20.csv` | `3203a21bb069021befc6365499b06045db1cfb7d7ffbee2897e7b2c923e1c772` | 15988 | 2026-09-14T08:21:55Z |
| 2024-01 | 2024-01-17 | CURRENT | `VX_current_2024-01-17.csv` | `c33e7eacdcbc80f3a52bd021019e41f9a22d92754a0c2c224f3d2a2f4db4b069` | 15792 | 2026-09-14T08:21:56Z |
| 2024-02 | 2024-02-14 | CURRENT | `VX_current_2024-02-14.csv` | `df87152acdc324ac6f7878833173fb393177b2054fba519c936bbd0c6605c944` | 15705 | 2026-09-14T08:21:58Z |
| 2024-03 | 2024-03-20 | CURRENT | `VX_current_2024-03-20.csv` | `d40ceba875932194c2ae69e7416755bd51d9a5eddc33d0f51cd2bed76ebd8277` | 15814 | 2026-09-14T08:21:59Z |
| 2024-04 | 2024-04-17 | CURRENT | `VX_current_2024-04-17.csv` | `60c15395c50f5451ee2f5df1d6827bb7e4a9025854f78f2581991ebde8b828f3` | 15812 | 2026-09-14T08:22:00Z |
| 2024-05 | 2024-05-22 | CURRENT | `VX_current_2024-05-22.csv` | `e8440ac8098644e41d1a1aeba7cc026252a0616fd063766e98c15a1d4ba65e60` | 16289 | 2026-09-14T08:22:02Z |
| 2024-06 | 2024-06-18 | CURRENT | `VX_current_2024-06-18.csv` | `b4573e89dc71fed7b7c8edd67dee89eec915c06d45a6c151a081449e07555d52` | 15727 | 2026-09-14T08:22:03Z |
| 2024-07 | 2024-07-17 | CURRENT | `VX_current_2024-07-17.csv` | `0c17e6acd5dbdf555d9739f81858ba3bb71082553e5c4b52d2de5b8f106f4164` | 15660 | 2026-09-14T08:22:04Z |
| 2024-08 | 2024-08-21 | CURRENT | `VX_current_2024-08-21.csv` | `7dda0ad59d4c66f9bfe50b473349e710447188c80347dc103483c9511f5a8900` | 16063 | 2026-09-14T08:22:04Z |
| 2024-09 | 2024-09-18 | CURRENT | `VX_current_2024-09-18.csv` | `d607740411fdf401a1a6eda8a6fceb9f130f285bb04efb85fb275794bcc2afe6` | 15691 | 2026-09-14T08:22:06Z |
| 2024-10 | 2024-10-16 | CURRENT | `VX_current_2024-10-16.csv` | `9a30d119303106c1a971aee8e3a718a8a65b98aa9a444b6f3665988fe3d8c667` | 15935 | 2026-09-14T08:22:07Z |
| 2024-11 | 2024-11-20 | CURRENT | `VX_current_2024-11-20.csv` | `18068d634bfce677ce8904d013b5c52e2f8c949c88b77768a4c49bca6ad9c3b7` | 16348 | 2026-09-14T08:22:08Z |
| 2024-12 | 2024-12-18 | CURRENT | `VX_current_2024-12-18.csv` | `d67e4ced59a4e85e30c381d4a1578e16fce47c28ee8b16e1df885beddd4c907a` | 15868 | 2026-09-14T08:22:10Z |
| 2025-01 | 2025-01-22 | CURRENT | `VX_current_2025-01-22.csv` | `d2c75bbfaef1bebf310fa08b2b1bc014853856d5abb7c653fa854624174a7494` | 16056 | 2026-09-14T08:22:12Z |
| 2025-02 | 2025-02-19 | CURRENT | `VX_current_2025-02-19.csv` | `ad6b0d7108076e6e8f7b93f183fe246f8f7ef6a559e76d71f67b8f56d53bc654` | 15583 | 2026-09-14T08:22:13Z |
| 2025-03 | 2025-03-18 | CURRENT | `VX_current_2025-03-18.csv` | `faf37215efaccc8e64a66b7e3691fe8cf1075ac5708d76cb8e1dadb33c2b2ec6` | 15658 | 2026-09-14T08:22:14Z |
| 2025-04 | 2025-04-16 | CURRENT | `VX_current_2025-04-16.csv` | `b0e29d9f0714be57568f7774947f46f06f5dc14c3ff963be08aeec29ccb08322` | 15872 | 2026-09-14T08:22:16Z |
| 2025-05 | 2025-05-21 | CURRENT | `VX_current_2025-05-21.csv` | `5fdb6b068b3d263d60cf42003582d6fc19e667964037bec10bad3cf2cc0821d9` | 15869 | 2026-09-14T08:22:17Z |
| 2025-06 | 2025-06-18 | CURRENT | `VX_current_2025-06-18.csv` | `a43f1037452b6ec8273601cbe5dc43d5821b2c49be79d9f0ce9458cd06fe317e` | 15810 | 2026-09-14T08:22:18Z |
| 2025-07 | 2025-07-16 | CURRENT | `VX_current_2025-07-16.csv` | `ae0cc06f810f8d84cfe7de674439062ca1264e42dcecdf8c1b94c3da7ef90c47` | 15631 | 2026-09-14T08:22:20Z |
| 2025-08 | 2025-08-20 | CURRENT | `VX_current_2025-08-20.csv` | `5ff06fc719856ac1b43560515a8e8154cbf90915a69033b315464b5f3f6a98e8` | 15727 | 2026-09-14T08:22:22Z |
| 2025-09 | 2025-09-17 | CURRENT | `VX_current_2025-09-17.csv` | `d4efe5445722462c1949c673e5d575b797be2d259148b61b30fb1baec29516cd` | 15689 | 2026-09-14T08:22:23Z |
| 2025-10 | 2025-10-22 | CURRENT | `VX_current_2025-10-22.csv` | `12089242dbacf614f0e4ebebe42d5b4b967afb252c0553216a1175599bd6dc36` | 15919 | 2026-09-14T08:22:24Z |
| 2025-11 | 2025-11-19 | CURRENT | `VX_current_2025-11-19.csv` | `ddc4b95e078d0f7df0bcb63d559f64dc8e5f0653a8193372b4b1da164b4d9464` | 16019 | 2026-09-14T08:22:26Z |
| 2025-12 | 2025-12-17 | CURRENT | `VX_current_2025-12-17.csv` | `0567a34df3a617ea4a540c82def1e80108efbd8c74d87e49b5fab90e1c617b08` | 15944 | 2026-09-14T08:22:28Z |
| 2026-01 | 2026-01-21 | CURRENT | `VX_current_2026-01-21.csv` | `0b1403f9c4a541b7526ceef9718ec86ca7805b54ea72a075653d560970c9b266` | 16101 | 2026-09-14T08:22:29Z |
| 2026-02 | 2026-02-18 | CURRENT | `VX_current_2026-02-18.csv` | `212b9932dfd0296984c2c6ed4534eb88bbc9068f0aa49f0f16fd513dc578c4e8` | 15606 | 2026-09-14T08:22:30Z |
| 2026-03 | 2026-03-18 | CURRENT | `VX_current_2026-03-18.csv` | `2be0f20e3164571c36ab6d13766c24545f1436ce35c1a329a52f2f05250fbbb4` | 15780 | 2026-09-14T08:22:32Z |
| 2026-04 | 2026-04-15 | CURRENT | `VX_current_2026-04-15.csv` | `a22c1d90792a90d697a164ad8dcf988ff6655424a8e5d9f25a6400d441b86509` | 15795 | 2026-09-14T08:22:33Z |
| 2026-05 | 2026-05-19 | CURRENT | `VX_current_2026-05-19.csv` | `17d7de93dcaf63db1ae4e30032d98f50dc0c56f5dca6f1f64a750e8364e0d0c1` | 15784 | 2026-09-14T08:22:34Z |
| 2026-06 | 2026-06-17 | CURRENT | `VX_current_2026-06-17.csv` | `c661d08dbed936be0df4cf4c23d7a66d4c1d0d9277547f78fdd5ee4febacaaf0` | 15819 | 2026-09-14T08:22:36Z |
| 2026-07 | 2026-07-22 | CURRENT | `VX_current_2026-07-22.csv` | `7231559f0504e73b081f085c4d348b2aab30129aaee6ec1e9f11bad5a962af4e` | 15674 | 2026-09-14T08:22:38Z |
| 2026-08 | 2026-08-19 | CURRENT | `VX_current_2026-08-19.csv` | `714558fad23a2f0482efa3f949dfcfb4b2d74af019a0cf27c92b787ad6166948` | 15680 | 2026-09-14T08:22:39Z |
| 2026-09 | 2026-09-16 | CURRENT | `VX_current_2026-09-16.csv` | `851ebc11b2d1bd724230537211438a05cda0d29d0cd3fb5aeff54138e9d0ff79` | 15434 | 2026-09-14T08:22:40Z |
| 2026-10 | 2026-10-21 | CURRENT | `VX_current_2026-10-21.csv` | `1e521fbbfb8ac3b41a76f187f388abfdf9bf03b4617d201c2f1d7a88c95b7fd6` | 13496 | 2026-09-14T08:22:42Z |
| 2026-11 | 2026-11-18 | CURRENT | `VX_current_2026-11-18.csv` | `9d1e638ac84d2edc984b227b0bf6e5dc301050f3f4602e917bd5b5cb36e2310a` | 11789 | 2026-09-14T08:22:43Z |
| 2026-12 | 2026-12-16 | CURRENT | `VX_current_2026-12-16.csv` | `8fcfa1e223cdcf9a3aa5d71c5b310548f93198406b469477c7dee352cd6c337a` | 10086 | 2026-09-14T08:22:44Z |

*Recompute every hash before use. Chat-carried bytes are never a source of truth.*
