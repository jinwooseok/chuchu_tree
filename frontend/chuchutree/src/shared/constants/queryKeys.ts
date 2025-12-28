export const QUERY_KEYS = {
  temp: {
    all: ['temp'],
    list: ['temp', 'list'],
    byTag: (tagId: string) => ['temp', 'byTag', tagId],
  },
};
