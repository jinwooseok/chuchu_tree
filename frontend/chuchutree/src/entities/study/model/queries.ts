'use client';

import { useQuery } from '@tanstack/react-query';
import { studyApi } from '../api/study.api';
import { studyKeys } from './keys';

export const useMyStudies = () => {
  return useQuery({
    queryKey: studyKeys.myList(),
    queryFn: studyApi.getMyStudies,
  });
};
