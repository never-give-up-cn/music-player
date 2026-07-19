const SONGS = [
  // ======== 第一批 26首 ========
  {
    title: '兄弟难当 (DJ版)',
    artist: '杜歌、何鹏',
    file: '01-兄弟难当-DJ版.mp3'
  },
  {
    title: '爱情有时很残忍 (DJ曹操版)',
    artist: '孙方',
    file: '02-爱情有时很残忍-DJ曹操版.mp3'
  },
  {
    title: '花桥流水 (DJ阿卓、DJ阿龙版)',
    artist: '豆包、阿卓',
    file: '03-花桥流水-DJ阿卓阿龙版.mp3'
  },
  {
    title: '一路生花',
    artist: '温奕心',
    file: '04-一路生花.mp3'
  },
  {
    title: '凤凰展翅 (DJ小黑版)',
    artist: '司徒兰芳、DJ小黑',
    file: '05-凤凰展翅-DJ小黑版.mp3'
  },
  {
    title: '走天涯',
    artist: '降央卓玛',
    file: '06-走天涯.mp3'
  },
  {
    title: '哔哔哔',
    artist: 'Crayon Pop',
    file: '07-哔哔哔.mp3'
  },
  {
    title: '我是奶龙 (今夜星光闪闪)(DJ版)',
    artist: '奶龙',
    file: '08-我是奶龙-今夜星光闪闪-DJ版.mp3'
  },
  {
    title: '游京 (奋斗进行曲)',
    artist: 'DJ筱轩',
    file: '09-游京-奋斗进行曲.mp3'
  },
  {
    title: '等到花儿开 (DJ阿远版)',
    artist: '杭娇、DJ阿远',
    file: '10-等到花儿开-DJ阿远版.mp3'
  },
  {
    title: '夜夜夜漫长',
    artist: 'DJ小鱼儿',
    file: '11-夜夜夜漫长.mp3'
  },
  {
    title: '她会魔法吧',
    artist: 'DJ小鱼儿',
    file: '12-她会魔法吧.mp3'
  },
  {
    title: '你看到的我 (DJ版)',
    artist: '黄勇、任书怀',
    file: '13-你看到的我-DJ版.mp3'
  },
  {
    title: '快乐阿拉蕾',
    artist: '邵雨涵',
    file: '14-快乐阿拉蕾.mp3'
  },
  {
    title: 'La La Love On My Mind',
    artist: 'Ann Winsborn',
    file: '15-La La Love On My Mind.mp3'
  },
  {
    title: '蹦吧啦 Bo Ba La (DJ版)',
    artist: '莎莎',
    file: '16-蹦吧啦-Bo Ba La-DJ版.mp3'
  },
  {
    title: '秒针 (DJ R7版)',
    artist: '阿梨粤、R7',
    file: '17-秒针-DJ R7版.mp3'
  },
  {
    title: '大风在刮大雪在下 (合唱团版)',
    artist: '六小乐',
    file: '18-大风在刮大雪在下-合唱团版.mp3'
  },
  {
    title: 'Like I Love You',
    artist: 'R.I.O.',
    file: '19-Like I Love You.mp3'
  },
  {
    title: '不变的音乐',
    artist: '王绎龙',
    file: '20-不变的音乐.mp3'
  },
  {
    title: '危险派对 (Live)',
    artist: 'Mr.岑 / 海山来了',
    file: '21-危险派对-Live.mp3'
  },
  {
    title: '快乐阿拉蕾',
    artist: '邵雨涵',
    file: '22-快乐阿拉蕾.mp3'
  },
  {
    title: '清明上河图',
    artist: 'dj友乾',
    file: '23-清明上河图.mp3'
  },
  {
    title: '无人扶我青云志 我自踏雪至山巅 (2025)',
    artist: 'Jonice',
    file: '24-无人扶我青云志-我自踏雪至山巅-2025.mp3'
  },
  {
    title: 'DJ TO MUCH BEER MANGKANE (DJ版)',
    artist: 'DJ Banjar',
    file: '25-DJ TO MUCH BEER MANGKANE-DJ版.mp3'
  },
  {
    title: '龙的传人',
    artist: '王力宏',
    file: '26-龙的传人.mp3'
  },
  // ======== 第二批 27首 ========
  {
    title: '落了白 (DJ小金版)',
    artist: 'bluesky',
    file: '27-落了白-DJ小金版.mp3'
  },
  {
    title: '只要平凡',
    artist: '张杰、张碧晨',
    file: '28-只要平凡.mp3'
  },
  {
    title: 'Brother Louie',
    artist: 'Modern Talking',
    file: '29-Brother Louie.mp3'
  },
  {
    title: '天下 (男女合唱版)',
    artist: '崇阳范冰水、张智宸',
    file: '30-天下-男女合唱版.mp3'
  },
  {
    title: 'Better Apart',
    artist: 'Jai Wolf、Dresage',
    file: '31-Better Apart.mp3'
  },
  {
    title: '美丽的神话 (0.9xDJ加强版)',
    artist: 'DJ科目三',
    file: '32-美丽的神话-DJ加强版.mp3'
  },
  {
    title: '新套马杆',
    artist: '乌兰托娅',
    file: '33-新套马杆.mp3'
  },
  {
    title: '画你 (恒大歌舞团)',
    artist: '科尔沁夫',
    file: '34-画你-恒大歌舞团.mp3'
  },
  {
    title: '都说 (DJ何鹏版)',
    artist: '龙梅子、老猫、何鹏',
    file: '35-都说-DJ何鹏版.mp3'
  },
  {
    title: '战马 (DJ默涵版)',
    artist: '崔伟立、DJ默涵',
    file: '36-战马-DJ默涵版.mp3'
  },
  {
    title: '百万个吻',
    artist: '陈明真',
    file: '37-百万个吻.mp3'
  },
  {
    title: '报喜财神爷',
    artist: '塘小小',
    file: '38-报喜财神爷.mp3'
  },
  {
    title: '好心态带来好运气',
    artist: '青冉',
    file: '39-好心态带来好运气.mp3'
  },
  {
    title: '天真的橡皮 (DJ版)',
    artist: '白水寒、DJ Wave',
    file: '40-天真的橡皮-DJ版.mp3'
  },
  {
    title: '歌在飞',
    artist: '苏勒亚其其格',
    file: '41-歌在飞.mp3'
  },
  {
    title: '与天空比个耶',
    artist: '姜雨涵',
    file: '42-与天空比个耶.mp3'
  },
  {
    title: '套马杆',
    artist: '乌兰托娅',
    file: '43-套马杆.mp3'
  },
  {
    title: '小米进行曲',
    artist: 'Gumpert!',
    file: '44-小米进行曲.mp3'
  },
  {
    title: '逃之夭夭 (DJheap九天版)',
    artist: '张禾禾、DJheap九天',
    file: '45-逃之夭夭-DJheap九天版.mp3'
  },
  {
    title: '夜夜夜夜叙 (DJ版)',
    artist: '张鑫雨',
    file: '46-夜夜夜夜叙-DJ版.mp3'
  },
  {
    title: '过火 (女声版)(DJ怪仔版)',
    artist: '子非鱼',
    file: '47-过火-女声版-DJ怪仔版.mp3'
  },
  {
    title: '漫步人生路',
    artist: '浅影阿',
    file: '48-漫步人生路.mp3'
  },
  {
    title: 'Sweet but Psycho',
    artist: 'Ava Max',
    file: '49-Sweet but Psycho.mp3'
  },
  {
    title: '星月神话',
    artist: '金莎',
    file: '50-星月神话.mp3'
  },
  {
    title: 'Boom, Boom, Boom, Boom!!',
    artist: 'Vengaboys',
    file: '51-Boom Boom Boom Boom.mp3'
  },
  {
    title: 'Everytime We Touch (DJ京仔版)',
    artist: 'DJ京仔、Natalie Horler',
    file: '52-Everytime We Touch-DJ京仔版.mp3'
  },
  {
    title: '外婆的澎湖湾 (DJ阿卓、DJ阿龙版)',
    artist: '1个球、阿卓',
    file: '53-外婆的澎湖湾-DJ阿卓阿龙版.mp3'
  },
  // ======== 第三批 27首 ========
  {
    title: '如愿 (而我将爱你所爱的人间)',
    artist: '小野来了',
    file: '54-如愿-而我将爱你所爱的人间.mp3'
  },
  {
    title: 'Baby It\'s Both (Tick-Tack English Ver.)',
    artist: 'ILLIT、Ava Max',
    file: '55-Baby It\'s Both.mp3'
  },
  {
    title: 'Girl In The Mirror',
    artist: 'Sophia Grace',
    file: '56-Girl In The Mirror.mp3'
  },
  {
    title: '花开的时候你就来看我',
    artist: '阿宝、张冬玲',
    file: '57-花开的时候你就来看我.mp3'
  },
  {
    title: '列车开往春天 (Remix)(DJ沈乐版)',
    artist: '就是南方凯、DJ沈乐',
    file: '58-列车开往春天-DJ沈乐版.mp3'
  },
  {
    title: '小米进行曲 (专属BGM)',
    artist: 'XSWLO',
    file: '59-小米进行曲-专属BGM.mp3'
  },
  {
    title: '猛男卡点舞',
    artist: 'M6、神拽',
    file: '60-猛男卡点舞.mp3'
  },
  {
    title: '自由飞翔',
    artist: '凤凰传奇',
    file: '61-自由飞翔.mp3'
  },
  {
    title: '鲸落 (莫小斯DJ版)',
    artist: '润姝',
    file: '62-鲸落-莫小斯DJ版.mp3'
  },
  {
    title: '被驯服的象',
    artist: '蔡健雅',
    file: '63-被驯服的象.mp3'
  },
  {
    title: '说书人',
    artist: '暗杠、寅子',
    file: '64-说书人.mp3'
  },
  {
    title: '人不可貌相 (DJ何鹏版)',
    artist: '郭玲、何鹏',
    file: '65-人不可貌相-DJ何鹏版.mp3'
  },
  {
    title: 'Everytime We Touch (DJ MAMUSUONA版)',
    artist: 'Cascada',
    file: '66-Everytime We Touch-DJ MAMUSUONA版.mp3'
  },
  {
    title: '皇后大道东',
    artist: '罗大佑',
    file: '67-皇后大道东.mp3'
  },
  {
    title: '天使的翅膀 (Live)',
    artist: '李悟小礼物',
    file: '68-天使的翅膀-Live.mp3'
  },
  {
    title: '倍儿爽',
    artist: '大张伟',
    file: '69-倍儿爽.mp3'
  },
  {
    title: '伤不起',
    artist: '王麟、老猫',
    file: '70-伤不起.mp3'
  },
  {
    title: '我的楼兰',
    artist: '云朵',
    file: '71-我的楼兰.mp3'
  },
  {
    title: '西海情歌',
    artist: '降央卓玛',
    file: '72-西海情歌-降央卓玛.mp3'
  },
  {
    title: '水手',
    artist: '郑智化',
    file: '73-水手.mp3'
  },
  {
    title: '美丽的神话',
    artist: '成龙、金喜善',
    file: '74-美丽的神话.mp3'
  },
  {
    title: '梦的光点',
    artist: '王心凌',
    file: '75-梦的光点.mp3'
  },
  {
    title: '快乐崇拜',
    artist: '潘玮柏、张韶涵',
    file: '76-快乐崇拜.mp3'
  },
  {
    title: '踏浪',
    artist: '徐怀钰',
    file: '77-踏浪.mp3'
  },
  {
    title: '西海情歌',
    artist: '刀郎',
    file: '78-西海情歌-刀郎.mp3'
  },
  {
    title: '快乐崇拜',
    artist: '潘玮柏、张韶涵',
    file: '79-快乐崇拜.mp3'
  },
  {
    title: '因为爱情 (独唱版)',
    artist: '覆予',
    file: '80-因为爱情-独唱版.mp3'
  }
];
