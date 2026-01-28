import { styled } from '@apache-superset/core/ui';

const CollapsedRightRail = styled.div`
  width: 100%;
  height: 100%;
  background-color: ${({ theme }) => theme.colorBgContainer};
  border-left: 1px solid ${({ theme }) => theme.colorBorder};
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;

  &:hover {
    background-color: ${({ theme }) => theme.colorBgLayout};
  }
`;

export default CollapsedRightRail;
