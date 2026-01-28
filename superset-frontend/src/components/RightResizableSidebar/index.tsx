/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */
import { FC, ReactNode } from 'react';
import { Resizable } from 're-resizable';
import { styled } from '@apache-superset/core/ui';
import useStoredSidebarWidth from '../ResizableSidebar/useStoredSidebarWidth';

const ResizableWrapper = styled.div<{ topOffset: number; height: string }>`
  /* Grid Layout handles positioning */
  height: ${({ height }) => height};
  background-color: ${({ theme }) => theme.colorBgContainer};
  border-left: 1px solid ${({ theme }) => theme.colorBorder};
  box-shadow: -4px 0 12px 0 rgba(0, 0, 0, 0.1);

  :hover .sidebar-resizer::after {
    background-color: ${({ theme }) => theme.colorPrimary};
  }

  .sidebar-resizer {
    z-index: 1001;
    left: 0 !important;
    width: 10px;
  }

  .sidebar-resizer::after {
    display: block;
    content: '';
    width: 1px;
    height: 100%;
    margin: 0 auto;
    background-color: ${({ theme }) => theme.colorBorder};
  }
`;

type Props = {
  id: string;
  initialWidth: number;
  enable: boolean;
  minWidth?: number;
  maxWidth?: number;
  children: (width: number) => ReactNode;
  onResize?: (width: number) => void;
  topOffset?: number;
  height?: string;
};

const RightResizableSidebar: FC<Props> = ({
  id,
  initialWidth,
  minWidth,
  maxWidth,
  enable,
  children,
  onResize,
  topOffset = 110,
  height = 'calc(100vh - 110px)',
}) => {
  const [width, setWidth] = useStoredSidebarWidth(id, initialWidth);

  return (
    <>
      <ResizableWrapper
        style={{ width: width }}
        topOffset={topOffset}
        height={height}
      >
        <Resizable
          enable={{ left: enable }}
          handleClasses={{
            left: 'sidebar-resizer',
            right: 'hidden',
            top: 'hidden',
            bottom: 'hidden',
            bottomRight: 'hidden',
            bottomLeft: 'hidden',
            topLeft: 'hidden',
            topRight: 'hidden',
          }}
          size={{ width, height: '100%' }}
          minWidth={minWidth}
          maxWidth={maxWidth}
          onResize={(e, direction, ref, d) => {
            const newWidth = width + d.width;
            if (onResize) onResize(newWidth);
          }}
          onResizeStop={(e, direction, ref, d) => {
            const newWidth = width + d.width;
            setWidth(newWidth);
            if (onResize) onResize(newWidth);
          }}
        >
          {children(width)}
        </Resizable>
      </ResizableWrapper>
    </>
  );
};

export default RightResizableSidebar;
