const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  WidthType, BorderStyle, AlignmentType, ShadingType, VerticalAlign,
  HeadingLevel, Header, Footer, PageNumber, NumberFormat,
} = require("docx");
const fs = require("fs");

const F_HEI = "FZLanTingHeiS-DB1-GB";   // 方正兰亭中粗黑(标题/强调)
const F_BODY = "FZLanTingHeiS-R-GB";    // 方正兰亭黑(正文)

const C_DARK = "1F4E79";    // 章节深蓝
const C_BAND = "DEEBF7";    // 歌词条浅蓝
const C_NOTE = "F2F2F2";    // 说明浅灰
const C_GREY = "595959";
const C_LINE = "BFBFBF";

const fontOf = (name) => ({ ascii: name, eastAsia: name, hAnsi: name });

const noBorder = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const thinBorder = { style: BorderStyle.SINGLE, size: 4, color: C_LINE };
const cellBorders = { top: thinBorder, bottom: thinBorder, left: thinBorder, right: thinBorder };
const cellMargins = { top: 70, bottom: 70, left: 110, right: 110 };

const CONTENT_W = 10006; // 11906 - 950*2
const W_LEFT = 1750;
const W_RIGHT = CONTENT_W - W_LEFT;

// ---------------- 数据 ----------------
const meta = [
  ["歌曲时长", "3分32秒"],
  ["拍摄规格", "4K · 16:9"],
  ["拍摄安排", "预计3个拍摄日,具体以贵方场地及出镜人员协调情况为准"],
  ["核心视觉符号", "微笑、青春阳光、桂林山水、微笑堂"],
  ["主线设定", "不设置固定主角,以员工、顾客、朋友、长者与亲子共同组成城市群像,通过不同人物在微笑堂中的真实片段,呈现一座城的温暖记忆。"],
  ["执行说明", "实拍集中在微笑堂门店内部、门口及外立面;桂林风景与品牌历史使用经贵方授权的素材呈现。全片以固定镜头和简单跟拍为主,后期按歌曲顺序直接切换画面。新增1个拍摄日采集笑脸照片及拍摄花絮,片尾制作笑脸矩阵组成\u201c微笑堂\u201d三个字,并附15至20秒拍摄花絮。"],
];

const sections = [
  { title: "一、前奏(0:00-0:10)", items: [
    { time: "0:00-0:10", lyric: "(前奏音乐 · 建立城市氛围)", shots: [
      "桂林清晨或城市苏醒的代表性画面,以2至3个经授权的风景素材建立城市氛围。",
      "固定机位拍摄微笑堂外立面、招牌及门前人流,交代故事发生地点。",
      "标题字样缓缓浮现:\u201c微笑与城\u201d。",
    ]},
  ]},
  { title: "二、主歌A(0:10-0:45)", items: [
    { time: "0:10-0:18", lyric: "清晨的漓江泛起微光,十字街头有座会笑的地方", shots: [
      "先后使用桂林山水授权素材、十字街环境和微笑堂楼体画面。",
      "一组年轻顾客从街口走向微笑堂,抬头看向招牌,自然露出微笑。",
    ]},
    { time: "0:18-0:27", lyric: "门前的桂花岁岁飘香,每一张笑脸都化作阳光", shots: [
      "桂花、绿植或晨光落在门店玻璃上的细节特写。",
      "不同年龄的顾客陆续进入商场,员工微笑致意,顾客回以微笑。",
      "连续拍摄顾客与员工的笑脸特写,按照歌曲节奏直接剪接。",
    ]},
    { time: "0:27-0:35", lyric: "从第一声问候开始绽放,把平凡日子酿成希望", shots: [
      "员工开业前整理仪容、佩戴工牌、检查着装。",
      "门口早迎宾的画面:问候、欢迎手势。",
    ]},
    { time: "0:35-0:45", lyric: "我甄选好物静待你的徜徉,每次相逢将你我内心点亮", shots: [
      "员工整理商品、擦拭柜台、摆正陈列。",
      "会员中心或服务台微笑接待顾客。",
      "导购为顾客介绍商品或指引方向,双方自然交流。",
    ]},
  ]},
  { title: "三、副歌(0:45-1:23)", items: [
    { time: "0:45-0:49", lyric: "微笑同城,美好同框", shots: [
      "固定机位拍摄商场中庭,不同人物从画面中自然经过并相互微笑。",
    ]},
    { time: "0:49-0:53", lyric: "我们一起写下的时光", shots: [
      "导购将商品递给顾客,双方目光交流并微笑。",
    ]},
    { time: "0:53-0:58", lyric: "山高水长,青春不散场", shots: [
      "两位年轻朋友挽手同行,穿过商场通道并轻松交谈。",
    ]},
    { time: "0:58-1:02", lyric: "微笑堂,给你温暖的光", shots: [
      "化妆品区内,导购举镜展示试妆效果,顾客满意微笑。",
    ]},
    { time: "1:02-1:07", lyric: "微笑与城,梦在身旁", shots: [
      "三位朋友在商场内挽手购物,边走边交流,相视而笑。",
    ]},
    { time: "1:07-1:16", lyric: "每一步都向着前方,陪伴城市我们同成长", shots: [
      "不同业种员工分成若干小组,在各自岗位面对镜头微笑挥手。",
      "简单跟拍一组顾客继续前行,员工在各自岗位微笑示意。",
    ]},
    { time: "1:16-1:23", lyric: "微笑堂,陪你把未来照亮", shots: [
      "分别拍摄中庭灯光、楼层空间和微笑堂外立面,按顺序直接剪接。",
    ]},
  ]},
  { title: "四、主歌B(1:23-1:58)", items: [
    { time: "1:23-1:30", lyric: "穿过熙熙攘攘的街巷,心中方向总有微笑堂", shots: [
      "简单跟拍两位顾客穿过商场通道与门口人流。",
      "另拍一位员工走出门店后回头看向微笑堂招牌,车流与行人作为自然背景。",
    ]},
    { time: "1:30-1:40", lyric: "你说这里是青春的存档,我说这里是家的延长", shots: [
      "两位年轻顾客在微笑堂内的肯德基就座用餐,自然分享餐点与笑容;画面突出广西首家肯德基的历史记忆。",
      "顾客在家电区选购冰箱或彩电,导购在旁进行简洁介绍,捕捉顾客查看产品细节的自然状态。",
    ]},
    { time: "1:40-1:50", lyric: "从第一份礼物到地久天长,从青涩模样到成熟脸庞", shots: [
      "一对银发夫妻在珠宝区慢慢挑选商品。",
      "老先生为老太太试戴项链,两人通过镜中目光相视而笑。",
    ]},
    { time: "1:50-1:58", lyric: "一分初心始终不曾变样,把万千美好送到你的身旁", shots: [
      "由贵方协调真实服务场景:床品区员工上门为顾客铺设床单、整理床品,拍摄手部与服务细节。",
      "由贵方协调真实服务场景:服装区导购将挑选好的服装送至顾客家中,供顾客试穿或查看搭配;以递送和交流的自然镜头呈现。",
    ]},
  ]},
  { title: "五、副歌B(1:58-2:35)", items: [
    { time: "1:58-2:02", lyric: "微笑与城,美好同框", shots: [
      "贵方提供的店庆、公益或营销活动照片与视频组成短蒙太奇。",
    ]},
    { time: "2:02-2:07", lyric: "我们一起写下的时光", shots: [
      "历年周年庆签到、切蛋糕、员工合影等授权素材按时间顺序直接呈现。",
    ]},
    { time: "2:07-2:11", lyric: "山高水长,青春不散场", shots: [
      "老旧照片集锦:微笑堂6楼美食街、电玩城照片。",
    ]},
    { time: "2:11-2:16", lyric: "微笑堂,给你温暖的光", shots: [
      "微笑堂的公益、爱心类活动视频(上门办卡或护理外拓活动)。",
    ]},
    { time: "2:16-2:20", lyric: "微笑与城,梦在身旁", shots: [
      "员工与顾客共同观看历史照片或活动展板,随后直接接入对应的历史素材。",
    ]},
    { time: "2:20-2:25", lyric: "每一步都向着前方", shots: [
      "员工布置物料、筹办活动画面。",
    ]},
    { time: "2:25-2:29", lyric: "陪伴城市我们同成长", shots: [
      "各种誓师大会、新年大会的视频素材。",
    ]},
    { time: "2:29-2:35", lyric: "微笑堂,陪你把未来照亮", shots: [
      "微笑堂楼体、招牌与周边城市人流共同入画。",
    ]},
  ]},
  { title: "六、念白(2:35-2:47)",
    note: "念白声音直接使用歌曲原声,出镜人物无需对口型。各句按照成曲中的实际落点对应以下画面,画面之间直接剪接。",
    items: [
    { time: "念白", lyric: "一城山水", shots: [
      "使用1个经授权的桂林山水代表性画面。",
    ]},
    { time: "念白", lyric: "一城烟火", shots: [
      "固定机位拍摄微笑堂门口、招牌与自然经过的人流。",
    ]},
    { time: "念白", lyric: "如果桂林是一张笑脸", shots: [
      "员工在服务台或专柜面向顾客自然微笑。",
    ]},
    { time: "念白", lyric: "我们就是最暖的那一帧", shots: [
      "保卫部操练、物业部员工检修画面。",
    ]},
    { time: "念白", lyric: "不管生活如何流转", shots: [
      "收银部员工练操。",
    ]},
    { time: "念白", lyric: "微笑堂的灯火永远为你点亮", shots: [
      "固定机位拍摄中庭灯光或微笑堂夜景招牌,直接进入最后一段副歌。",
    ]},
  ]},
  { title: "七、副歌+结尾(2:47-3:32)", items: [
    { time: "2:47-3:05", lyric: "微笑与城,美好同框 / 我们一起写下的时光 / 山高水长,青春不散场 / 微笑堂,给你温暖的光", shots: [
      "亲子、朋友、银发夫妻、顾客和员工分别面对镜头自然微笑,每组拍摄一个正面镜头。",
      "员工分成若干小组,每组只完成一次微笑和一次挥手。",
      "不同人物的笑脸特写按照歌曲顺序直接剪接,最后接一组员工与顾客共同微笑。",
    ]},
    { time: "3:05-3:09", lyric: "微笑与城,梦在身旁", shots: [
      "所有已出镜人物在中庭或正门口完成一次集中合影,面对镜头微笑挥手。",
    ]},
    { time: "3:09-3:14", lyric: "每一步都向着前方", shots: [
      "员工分组站成一排,镜头平扫手部与统一指引手势。",
    ]},
    { time: "3:14-3:18", lyric: "陪伴城市我们同成长", shots: [
      "固定机位分别拍摄中庭灯饰、员工与顾客,按顺序直接剪接。",
    ]},
    { time: "3:18-3:32", lyric: "微笑堂,陪你把未来照亮", shots: [
      "员工、顾客、朋友、长者与亲子依次给出近景微笑;另拍一条固定广角,所有出镜人物共同挥手。",
      "固定机位拍摄微笑堂外立面与城市夜色,作为歌曲部分的最后一个实拍画面。",
      "采集员工、顾客及已出镜人物的正面笑脸照片。后期将多张笑脸通过重复排列与矩阵合成,逐步汇聚成\u201c微笑堂\u201d三个字。",
      "\u201c微笑堂\u201d三个字完整呈现后,加入大商集团Logo、微笑堂Logo及片名\u201c微笑与城\u201d,定格结束歌曲部分。",
    ]},
    { time: "3:32后", lyric: "拍摄花絮(15-20秒)", shots: [
      "选取现场准备、人物互动、笑场、整理服装、调整机位及集体挥手等自然片段。",
      "花絮采用现场同期声或保留轻音乐,画面按照拍摄顺序直接剪接。",
      "花絮结尾再次出现微笑堂Logo及\u201c感谢参与\u201d字样,完成全片。",
    ]},
  ]},
  { title: "八、第三拍摄日新增素材清单", items: [
    { time: "素材一", lyric: "笑脸矩阵素材", shots: [
      "分别采集员工、顾客、朋友、长者及亲子等出镜人物的正面笑脸照片。",
      "笑脸照片使用统一机位、相近景别和简洁背景拍摄,保证后期矩阵排列清晰。",
      "现场完成单人笑脸、双人笑脸及小组合影三类素材,后期可通过重复排列形成大规模笑脸墙。",
    ]},
    { time: "素材二", lyric: "15-20秒拍摄花絮素材", shots: [
      "记录设备准备、灯光调整、人物候场、整理服装及导演沟通等现场过程。",
      "记录人物自然互动、笑场、重复拍摄及拍摄完成后的轻松状态。",
      "补拍全体出镜人员面对花絮机位挥手或说\u201c拍摄完成\u201d,作为花絮结尾备用画面。",
    ]},
  ]},
];

// ---------------- 构件 ----------------
const run = (text, opts = {}) => new TextRun({
  text, font: fontOf(opts.bold ? F_HEI : F_BODY),
  size: opts.size ?? 20, color: opts.color ?? "000000",
  bold: !!opts.bold, italics: !!opts.italics,
});

function metaTable() {
  return new Table({
    width: { size: CONTENT_W, type: WidthType.DXA },
    columnWidths: [W_LEFT, W_RIGHT],
    rows: meta.map(([k, v]) => new TableRow({
      cantSplit: true,
      children: [
        new TableCell({
          width: { size: W_LEFT, type: WidthType.DXA },
          shading: { type: ShadingType.CLEAR, fill: "E8EEF5" },
          margins: cellMargins, verticalAlign: VerticalAlign.CENTER, borders: cellBorders,
          children: [new Paragraph({
            spacing: { line: 300, before: 0, after: 0 },
            children: [run(k, { bold: true, size: 20 })],
          })],
        }),
        new TableCell({
          width: { size: W_RIGHT, type: WidthType.DXA },
          margins: cellMargins, verticalAlign: VerticalAlign.CENTER, borders: cellBorders,
          children: [new Paragraph({
            spacing: { line: 300, before: 0, after: 0 },
            children: [run(v, { size: 20 })],
          })],
        }),
      ],
    })),
  });
}

function sectionTitleRow(title) {
  return new TableRow({
    cantSplit: true,
    children: [new TableCell({
      columnSpan: 2,
      shading: { type: ShadingType.CLEAR, fill: C_DARK },
      margins: { top: 150, bottom: 150, left: 110, right: 110 },
      borders: cellBorders,
      children: [new Paragraph({
        heading: HeadingLevel.HEADING_1,
        spacing: { line: 300, before: 0, after: 0 },
        children: [run(title, { bold: true, size: 24, color: "FFFFFF" })],
      })],
    })],
  });
}

function noteRow(note) {
  return new TableRow({
    cantSplit: true,
    children: [new TableCell({
      columnSpan: 2,
      shading: { type: ShadingType.CLEAR, fill: C_NOTE },
      margins: cellMargins, borders: cellBorders,
      children: [new Paragraph({
        spacing: { line: 280, before: 0, after: 0 },
        children: [run("说明:" + note, { size: 18, color: C_GREY })],
      })],
    })],
  });
}

function bandRow(time, lyric) {
  return new TableRow({
    cantSplit: true,
    children: [
      new TableCell({
        width: { size: W_LEFT, type: WidthType.DXA },
        shading: { type: ShadingType.CLEAR, fill: C_BAND },
        margins: cellMargins, verticalAlign: VerticalAlign.CENTER, borders: cellBorders,
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { line: 280, before: 0, after: 0 },
          children: [run(time, { bold: true, size: 20 })],
        })],
      }),
      new TableCell({
        width: { size: W_RIGHT, type: WidthType.DXA },
        shading: { type: ShadingType.CLEAR, fill: C_BAND },
        margins: cellMargins, verticalAlign: VerticalAlign.CENTER, borders: cellBorders,
        children: [new Paragraph({
          spacing: { line: 280, before: 0, after: 0 },
          children: [run(lyric, { bold: true, size: 20 })],
        })],
      }),
    ],
  });
}

function shotRow(idx, text) {
  return new TableRow({
    cantSplit: true,
    children: [
      new TableCell({
        width: { size: W_LEFT, type: WidthType.DXA },
        margins: cellMargins, verticalAlign: VerticalAlign.CENTER, borders: cellBorders,
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { line: 280, before: 0, after: 0 },
          children: [run("分镜" + idx, { size: 18, color: C_GREY })],
        })],
      }),
      new TableCell({
        width: { size: W_RIGHT, type: WidthType.DXA },
        margins: cellMargins, borders: cellBorders,
        children: [new Paragraph({
          spacing: { line: 280, before: 0, after: 0 },
          children: [run(text, { size: 20 })],
        })],
      }),
    ],
  });
}

function headerRow() {
  return new TableRow({
    tableHeader: true, cantSplit: true,
    children: ["时间 / 段落", "歌词 · 画面与分镜"].map((t, i) => new TableCell({
      width: { size: i === 0 ? W_LEFT : W_RIGHT, type: WidthType.DXA },
      shading: { type: ShadingType.CLEAR, fill: "404040" },
      margins: cellMargins, verticalAlign: VerticalAlign.CENTER, borders: cellBorders,
      children: [new Paragraph({
        alignment: i === 0 ? AlignmentType.CENTER : AlignmentType.LEFT,
        spacing: { line: 280, before: 0, after: 0 },
        children: [run(t, { bold: true, size: 19, color: "FFFFFF" })],
      })],
    })),
  });
}

function mainTable() {
  const rows = [headerRow()];
  for (const sec of sections) {
    rows.push(sectionTitleRow(sec.title));
    if (sec.note) rows.push(noteRow(sec.note));
    for (const item of sec.items) {
      rows.push(bandRow(item.time, item.lyric));
      item.shots.forEach((s, i) => rows.push(shotRow(i + 1, s)));
    }
  }
  return new Table({
    width: { size: CONTENT_W, type: WidthType.DXA },
    columnWidths: [W_LEFT, W_RIGHT],
    rows,
  });
}

// ---------------- 文档 ----------------
const doc = new Document({
  styles: {
    default: {
      document: { run: { font: fontOf(F_BODY), size: 20 } },
    },
  },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },
        margin: { top: 900, bottom: 1000, left: 950, right: 950, header: 500, footer: 500 },
        pageNumbers: { start: 1, formatType: NumberFormat.DECIMAL },
      },
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          alignment: AlignmentType.RIGHT,
          spacing: { line: 240, after: 0 },
          border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: C_LINE, space: 2 } },
          children: [run("《微笑与城》MV拍摄脚本与分镜 · 7000元群像执行版", { size: 17, color: C_GREY })],
        })],
      }),
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { line: 240, before: 0, after: 0 },
          children: [
            run("第 ", { size: 18, color: C_GREY }),
            new TextRun({ children: [PageNumber.CURRENT], font: fontOf(F_BODY), size: 18, color: C_GREY }),
            run(" 页,共 ", { size: 18, color: C_GREY }),
            new TextRun({ children: [PageNumber.TOTAL_PAGES], font: fontOf(F_BODY), size: 18, color: C_GREY }),
            run(" 页", { size: 18, color: C_GREY }),
          ],
        })],
      }),
    },
    children: [
      new Paragraph({
        heading: HeadingLevel.TITLE,
        alignment: AlignmentType.CENTER,
        spacing: { line: 320, before: 0, after: 80 },
        children: [run("《微笑与城》MV拍摄脚本与分镜", { bold: true, size: 40, color: C_DARK })],
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { line: 280, before: 0, after: 160 },
        children: [run("7000元群像执行版 · 服务场景调整", { size: 21, color: C_GREY })],
      }),
      metaTable(),
      new Paragraph({
        spacing: { line: 280, before: 140, after: 100 },
        children: [run("以下按歌曲顺序列出各时间段的画面安排与分镜,供现场执行使用。", { size: 19, color: C_GREY, italics: true })],
      }),
      mainTable(),
    ],
  }],
});

const OUT = "/Users/jacksun/Desktop/微笑堂资料/微笑与城MV拍摄脚本与分镜_A4打印版.docx";
Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(OUT, buf);
  console.log("WROTE", OUT, buf.length, "bytes");
});
