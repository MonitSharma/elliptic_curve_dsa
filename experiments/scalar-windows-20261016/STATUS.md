# Larger scalar tables: exact, no adoption

Windows18/20/21/22 all reproduce the independently protected4,096 pair fixture,
including24,576 coordinate values and zero/order/overflow/infinity cases.
Three fresh trials at one and eight workers are retained. At eight workers,
median times for262,144 pairs are0.560/0.511/0.522/0.545seconds respectively.
Window20 remains selected; larger tables offer no clear loaded-server gain.
All25 archived artifacts verify. The initial missing include-path build failure
and the corrected retry are preserved. No circuit or input semantics changed.
