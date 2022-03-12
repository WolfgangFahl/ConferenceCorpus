module.exports = function (title,description,acronym,inception) {
  return {
    labels: {
      en: title
    },
    descriptions: {
      en: description
    },
    aliases: {
      en: [
        acronym
      ]
    },
    claims: {
      // instance of: scientific conference series
      P31: 'Q47258130',
      // inception
      P571: {
        value: {
          time: inception,
          timezone: 0,
          before: 0,
          after: 0,
          precision: 9,
          calendarmodel: 'http://www.wikidata.org/entity/Q1985727'
        },
      },
      // short name
      P1813: {
        text: acronym,
        language: 'en'
      },
      // title
      P1476: {
        value: {
          text: title,
          language: 'en'
        },
      },
    },
  }
}
