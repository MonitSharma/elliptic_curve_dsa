## Verified update and research break · 21 October 2026

Latest official independent Toffoli minimum is **1464×746089=1092274296**,
[submission8d704a6b](https://api.ecdsa.fail/api/submissions/8d704a6b-659c-4d67-9bd0-f6862de9f617).
The complete benchmark passes all9024 shots and public source matches all207
source/17protected files. Globalproduct remains932057476; width minimum669.
Work is paused at human request. [Full handoff](RESEARCH_BREAK_2026-10-21.md)
separates all component/proxy/failed trials from verified scores. Existing plots
and pre-existing user changes were preserved; no diagnostic points were added.

# Current Pareto frontier

Public snapshot: **17 October 2026**, retrieved 12:36 Singapore time.

1,584 submissions · 1,241 eligible official scores · **45 nondominated resource pairs**.

**MonitSharma holds 4 current Pareto points including the minimum product and minimum Toffoli count.** Minimum width is 676 qubits (bulengerk).

Includes accepted submissions and rejections solely for failing to improve the scalar product. All included products equal peak qubits × rounded mean executed Toffolis. Benchmark failures, other rejection categories and claimed-only results are excluded. A passing finite packet does not prove correctness for all inputs.

![Current resource frontier](figures/leaderboard-frontier.png)

[Result details and provenance](leaderboard-results.md) · [Official source](https://api.ecdsa.fail/api/benchmarks/1ffb695a-309b-46b6-a728-2f97d8c7be74/submissions) · [Saved data](data/leaderboard/README.md)

| Qubits | Rounded Toffolis | Product | Solver | Submission |
|---:|---:|---:|---|---|
| 676 | 490,149,075 | 331,340,774,700 | bulengerk | [42ae2103](https://api.ecdsa.fail/api/submissions/42ae2103-575e-4f95-bbd5-ab2051a994f2) |
| 691 | 296,500,718 | 204,881,996,138 | jackylee0424 | [13c1e055](https://api.ecdsa.fail/api/submissions/13c1e055-7ffa-4115-a79c-8b42c53d79b3) |
| 698 | 291,612,614 | 203,545,604,572 | jackylee0424 | [f20716bf](https://api.ecdsa.fail/api/submissions/f20716bf-b03e-4101-ab81-46f286f232e2) |
| 718 | 284,765,142 | 204,461,371,956 | BitWonka | [b98ba940](https://api.ecdsa.fail/api/submissions/b98ba940-142f-4148-8f10-8df44a2c47d6) |
| 739 | 220,601,275 | 163,024,342,225 | BitWonka | [ae371a08](https://api.ecdsa.fail/api/submissions/ae371a08-0aaf-4be0-bd3c-6b9ff9e15955) |
| 770 | 115,382,810 | 88,844,763,700 | bulengerk | [978d89f5](https://api.ecdsa.fail/api/submissions/978d89f5-6938-48a3-b37a-b5131326e9e2) |
| 794 | 49,151,603 | 39,026,372,782 | gnuchev | [bb7c3804](https://api.ecdsa.fail/api/submissions/bb7c3804-b389-4d97-91fe-b3f69d10ccc0) |
| 795 | 37,846,519 | 30,087,982,605 | gnuchev | [93e11b9d](https://api.ecdsa.fail/api/submissions/93e11b9d-fcf7-4a7b-81fa-8733aa130f5c) |
| 796 | 29,886,875 | 23,789,952,500 | gnuchev | [a51637f6](https://api.ecdsa.fail/api/submissions/a51637f6-7068-4876-b58d-20aaf6e9a2d5) |
| 797 | 23,396,795 | 18,647,245,615 | gnuchev | [129115cd](https://api.ecdsa.fail/api/submissions/129115cd-5eab-45bb-b1a8-9faa883b1970) |
| 798 | 18,707,563 | 14,928,635,274 | gnuchev | [dff84426](https://api.ecdsa.fail/api/submissions/dff84426-5d3d-46fe-8d19-43842283cb4e) |
| 799 | 17,340,825 | 13,855,319,175 | gnuchev | [666b952b](https://api.ecdsa.fail/api/submissions/666b952b-4ba5-4a21-a279-d544b67bdea8) |
| 819 | 14,489,348 | 11,866,776,012 | gnuchev | [3e7f1342](https://api.ecdsa.fail/api/submissions/3e7f1342-4588-4a5f-a80e-f1b8187c657c) |
| 843 | 11,947,178 | 10,071,471,054 | jieyilong | [4a8ade44](https://api.ecdsa.fail/api/submissions/4a8ade44-9259-4e2d-bc80-91186c2a19ce) |
| 860 | 5,320,067 | 4,575,257,620 | jieyilong | [e536537a](https://api.ecdsa.fail/api/submissions/e536537a-49b4-4cb1-97ae-8fbe784955b6) |
| 870 | 4,931,026 | 4,289,992,620 | jieyilong | [255a6412](https://api.ecdsa.fail/api/submissions/255a6412-097d-4e7b-b597-6b116cd1675b) |
| 874 | 2,398,215 | 2,096,039,910 | jieyilong | [ae537372](https://api.ecdsa.fail/api/submissions/ae537372-a846-424e-b613-9c4038a0a46e) |
| 877 | 2,331,376 | 2,044,616,752 | jieyilong | [7be7b9a5](https://api.ecdsa.fail/api/submissions/7be7b9a5-99c3-4fd1-9d27-310f4f2d33c1) |
| 880 | 2,272,805 | 2,000,068,400 | jieyilong | [c56a97ad](https://api.ecdsa.fail/api/submissions/c56a97ad-27a2-4644-ae29-bfe42b386f6f) |
| 883 | 2,255,931 | 1,991,987,073 | jieyilong | [5da304d6](https://api.ecdsa.fail/api/submissions/5da304d6-799b-4caf-bd73-b9b7af4619e9) |
| 886 | 2,234,393 | 1,979,672,198 | jieyilong | [a29d49f7](https://api.ecdsa.fail/api/submissions/a29d49f7-22e0-48dc-918b-b8df8c7a25f6) |
| 888 | 2,226,549 | 1,977,175,512 | jieyilong | [be02266a](https://api.ecdsa.fail/api/submissions/be02266a-0fc6-453d-b422-a363804d64ba) |
| 889 | 2,223,969 | 1,977,108,441 | jieyilong | [8eb7104c](https://api.ecdsa.fail/api/submissions/8eb7104c-84fc-464a-b485-1385063933a7) |
| 893 | 2,218,127 | 1,980,787,411 | jieyilong | [457ccb7a](https://api.ecdsa.fail/api/submissions/457ccb7a-4436-4e8c-8e8c-f7d22c3c81b5) |
| 1,108 | 2,083,655 | 2,308,689,740 | gnuchev | [615ca7d3](https://api.ecdsa.fail/api/submissions/615ca7d3-55bc-43f6-b82a-5951630d15f3) |
| 1,109 | 1,983,705 | 2,199,928,845 | gnuchev | [07c7b502](https://api.ecdsa.fail/api/submissions/07c7b502-0b45-4784-9cbf-6e257bb1f78f) |
| 1,110 | 1,877,192 | 2,083,683,120 | gnuchev | [8070b00f](https://api.ecdsa.fail/api/submissions/8070b00f-da38-4513-89f1-09ab0f713b7d) |
| 1,111 | 1,785,244 | 1,983,406,084 | gnuchev | [28b7040d](https://api.ecdsa.fail/api/submissions/28b7040d-820a-49ed-bfff-6dc18cc2156e) |
| 1,112 | 1,739,356 | 1,934,163,872 | gnuchev | [c1c0da9f](https://api.ecdsa.fail/api/submissions/c1c0da9f-3038-4cde-b0e2-6820791b6fcc) |
| 1,133 | 1,460,511 | 1,654,758,963 | jieyilong | [1c0e0e91](https://api.ecdsa.fail/api/submissions/1c0e0e91-de6a-4348-bd4a-3b6351fdc70b) |
| 1,134 | 1,460,084 | 1,655,735,256 | gnuchev | [a21ec672](https://api.ecdsa.fail/api/submissions/a21ec672-90db-4ecf-ade0-892e526bc680) |
| 1,141 | 1,423,723 | 1,624,467,943 | jieyilong | [3d9ce591](https://api.ecdsa.fail/api/submissions/3d9ce591-8f26-4b76-8abf-0d41728e3939) |
| 1,142 | 1,415,790 | 1,616,832,180 | jieyilong | [3ab4f864](https://api.ecdsa.fail/api/submissions/3ab4f864-67ae-4aea-957b-bca4e5bd53b4) |
| 1,143 | 1,411,643 | 1,613,507,949 | jieyilong | [71b9cc45](https://api.ecdsa.fail/api/submissions/71b9cc45-8b14-4655-9b59-d6de5af1ceea) |
| 1,145 | 1,132,785 | 1,297,038,825 | gnuchev | [dd3621dc](https://api.ecdsa.fail/api/submissions/dd3621dc-a432-412b-bf9d-3c5d52774147) |
| 1,164 | 970,983 | 1,130,224,212 | gnuchev | [17250b2e](https://api.ecdsa.fail/api/submissions/17250b2e-ac81-4cb5-a4b3-a0029a8d5da4) |
| 1,170 | 946,553 | 1,107,467,010 | dysnasia | [b72ce1ae](https://api.ecdsa.fail/api/submissions/b72ce1ae-c5e0-46b8-a562-b5f1ac4d074a) |
| 1,171 | 945,839 | 1,107,577,469 | dysnasia | [a158447c](https://api.ecdsa.fail/api/submissions/a158447c-9c4d-4bcd-8cfa-fa2667508690) |
| 1,172 | 945,335 | 1,107,932,620 | jackylee0424 | [73c5e2a8](https://api.ecdsa.fail/api/submissions/73c5e2a8-f15c-4b01-a3ac-8d0ac1807391) |
| 1,173 | 944,566 | 1,107,975,918 | dysnasia | [1d602397](https://api.ecdsa.fail/api/submissions/1d602397-0e14-4314-8834-3e80db97b02c) |
| 1,174 | 943,826 | 1,108,051,724 | dysnasia | [ee410040](https://api.ecdsa.fail/api/submissions/ee410040-42fd-4a53-bcea-1150b7e2c5bf) |
| 1,234 | 761,121 | 939,223,314 | **MonitSharma** | [d7f69382](https://api.ecdsa.fail/api/submissions/d7f69382-4716-4b86-9fac-151c8bc581e4) |
| 1,464 | 753,771 | 1,103,520,744 | **MonitSharma** | [3f32acd2](https://api.ecdsa.fail/api/submissions/3f32acd2-71bf-4cc7-bae6-7407be97fe3b) |
| 1,468 | 753,721 | 1,106,462,428 | **MonitSharma** | [03be8e19](https://api.ecdsa.fail/api/submissions/03be8e19-ab3b-45c7-9c62-9d78970c4d95) |
| 1,556 | 753,694 | 1,172,747,864 | **MonitSharma** | [b99c9678](https://api.ecdsa.fail/api/submissions/b99c9678-5a68-49e8-a8b7-91fc6c383e37) |
