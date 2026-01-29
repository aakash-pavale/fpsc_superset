import { FC, useState, useRef, useEffect } from 'react';
import { t } from '@apache-superset/core';
import { styled, useTheme, css } from '@apache-superset/core/ui';
import { SupersetClient } from '@superset-ui/core';
import { Icons } from '@superset-ui/core/components/Icons';
import Markdown from 'markdown-to-jsx';
import { Loading } from '@superset-ui/core/components';

// @ts-ignore
const flobiLogo = require('src/assets/images/flobi_logo.png');

const ChatPanelContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: ${({ theme }) => theme.colorBgContainer};
  border-left: 1px solid ${({ theme }) => theme.colorBorder};
  box-shadow: -2px 0 4px 0 rgba(0, 0, 0, 0.1);
  overflow: hidden;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: ${({ theme }) => theme.sizeUnit * 4}px;
  background-color: ${({ theme }) => theme.colorBgContainer};
  color: ${({ theme }) => theme.colorText};
  font-size: ${({ theme }) => theme.fontSizeLG}px;
  font-weight: ${({ theme }) => theme.fontWeightStrong};
  border-bottom: 1px solid ${({ theme }) => theme.colorBorder};
  flex-shrink: 0;
`;

const TitleSection = styled.div`
  display: flex;
  align-items: center;
  gap: ${({ theme }) => theme.sizeUnit}px;
`;

const BetaLabel = styled.span`
  font-size: ${({ theme }) => theme.typography?.sizes?.s ?? 12}px;
  color: ${({ theme }) => theme.colorTextTertiary};
  font-weight: ${({ theme }) => theme.typography?.weights?.normal ?? 400};
`;

const RightSection = styled.div`
  display: flex;
  align-items: center;
  gap: ${({ theme }) => theme.sizeUnit * 2}px;
`;

const PoweredByContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  line-height: 1;
`;

const PoweredByText = styled.span`
  font-size: 8px;
  color: ${({ theme }) => theme.colorTextTertiary};
  margin-bottom: 2px;
`;

const LogoImage = styled.img`
  height: 16px;
  width: auto;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: ${({ theme }) => theme.sizeUnit * 2}px;
  &:hover {
    opacity: 0.8;
  }
`;

const Content = styled.div`
  flex: 1;
  padding: ${({ theme }) => theme.sizeUnit * 4}px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: ${({ theme }) => theme.sizeUnit * 3}px;
`;

const MessageBubble = styled.div<{ isUser: boolean }>`
  max-width: 85%;
  padding: ${({ theme }) => theme.sizeUnit * 3}px;
  border-radius: 12px;
  align-self: ${({ isUser }) => (isUser ? 'flex-end' : 'flex-start')};
  background-color: ${({ isUser, theme }) =>
    isUser ? theme.colorPrimary : theme.colorBgLayout};
  color: ${({ isUser, theme }) => (isUser ? '#fff' : theme.colorText)};
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  font-size: ${({ theme }) => theme.typography?.sizes?.s || 12}px;
  line-height: 1.5;

  & > div {
    overflow-x: auto;
  }

  /* Markdown Styles */
  p {
    margin-bottom: ${({ theme }) => theme.sizeUnit * 2}px;
    &:last-child {
      margin-bottom: 0;
    }
  }

  table {
    border-collapse: collapse;
    width: 100%;
    margin: ${({ theme }) => theme.sizeUnit * 2}px 0;
    font-size: 11px;
  }

  th,
  td {
    border: 1px solid ${({ theme }) => theme.colorBorder};
    padding: ${({ theme }) => theme.sizeUnit}px;
    text-align: left;
  }

  th {
    background-color: ${({ theme }) => theme.colorBgLayout};
    font-weight: bold;
  }

  code {
    background-color: ${({ theme }) => theme.colorBgLayout};
    padding: 2px 4px;
    border-radius: 2px;
    font-family: 'Source Code Pro', monospace;
  }

  pre {
    background-color: #2b2b2b;
    color: #f8f8f2;
    padding: ${({ theme }) => theme.sizeUnit * 2}px;
    border-radius: 4px;
    overflow-x: auto;

    code {
      background-color: transparent;
      color: inherit;
      padding: 0;
    }
  }
`;

const InputArea = styled.div`
  padding: ${({ theme }) => theme.sizeUnit * 4}px;
  border-top: 1px solid ${({ theme }) => theme.colorBorder};
  background-color: #fff;
  flex-shrink: 0;
  display: flex;
  gap: ${({ theme }) => theme.sizeUnit * 2}px;
`;

const StyledInput = styled.input`
  flex: 1;
  padding: ${({ theme }) => theme.sizeUnit * 2}px;
  border: 1px solid ${({ theme }) => theme.colorBorder};
  border-radius: 4px;
  font-size: 14px;

  &:focus {
    outline: none;
    border-color: ${({ theme }) => theme.colorPrimary};
    box-shadow: 0 0 0 2px ${({ theme }) => theme.colorPrimary}33;
  }
`;

const SendButton = styled.button`
  background-color: ${({ theme, disabled }) =>
    disabled ? theme.colorBgLayout : theme.colorPrimary};
  color: #fff;
  border: none;
  border-radius: 4px;
  padding: 0 ${({ theme }) => theme.sizeUnit * 3}px;
  cursor: ${({ disabled }) => (disabled ? 'not-allowed' : 'pointer')};
  font-weight: bold;
  transition: background-color 0.2s;

  &:hover {
    background-color: ${({ theme, disabled }) =>
    disabled ? theme.colorBgLayout : theme.colorPrimary};
    opacity: ${({ disabled }) => (disabled ? 1 : 0.9)};
  }
`;

interface AIChatPanelProps {
  onClose: () => void;
  dashboardId?: number | string;
}

const AIChatPanel: FC<AIChatPanelProps> = ({ onClose, dashboardId }) => {
  const theme = useTheme();
  const [messages, setMessages] = useState<
    Array<{ text: string; isUser: boolean }>
  >([
    {
      text: t('Welcome! How can I help you analyze this dashboard today?'),
      isUser: false,
    },
  ]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const contentRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (contentRef.current) {
      contentRef.current.scrollTop = contentRef.current.scrollHeight;
    }
  }, [messages, loading]);

  const handleSend = async () => {
    if (!inputText.trim() || loading) return;

    const userMessage = inputText;
    setMessages(prev => [...prev, { text: userMessage, isUser: true }]);
    setInputText('');
    setLoading(true);

    try {
      const { json } = await SupersetClient.post({
        endpoint: '/api/v1/ai_chat/query',
        jsonPayload: {
          dashboard_id: dashboardId || 0,
          prompt: userMessage,
        },
      });

      const responseText = json.result.response || 'No response';

      setMessages(prev => [...prev, { text: responseText, isUser: false }]);
    } catch (error) {
      console.error('AI Chat Error:', error);
      let errorMsg = t('Error connecting to AI Assistant.');
      if (error && typeof error === 'object' && 'message' in error) {
        errorMsg += ` ${(error as any).message}`;
      }
      setMessages(prev => [...prev, { text: errorMsg, isUser: false }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ChatPanelContainer>
      <Header>
        <TitleSection>
          {t('AI Assistant')}
          <BetaLabel>{t('(Beta)')}</BetaLabel>
        </TitleSection>
        <RightSection>
          <PoweredByContainer>
            <PoweredByText>{t('Powered by')}</PoweredByText>
            <LogoImage src={flobiLogo} alt="FLOBI ANALYTICS" />
          </PoweredByContainer>
          <CloseButton onClick={onClose}>
            <Icons.VerticalAlignTopOutlined
              iconSize="l"
              css={css`
                color: #666;
                transform: rotate(90deg);
              `}
            />
          </CloseButton>
        </RightSection>
      </Header>
      <Content ref={contentRef}>
        {messages.map((msg, idx) => (
          <MessageBubble key={idx} isUser={msg.isUser}>
            {msg.isUser ? (
              msg.text
            ) : (
              <Markdown options={{ forceBlock: true }}>{msg.text}</Markdown>
            )}
          </MessageBubble>
        ))}
        {loading && (
          <div style={{ alignSelf: 'flex-start', padding: 8 }}>
            <Loading position="inline" />
          </div>
        )}
      </Content>
      <InputArea>
        <StyledInput
          type="text"
          placeholder={t('Ask a question about your data...')}
          value={inputText}
          onChange={e => setInputText(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleSend()}
        />
        <SendButton onClick={handleSend} disabled={loading}>
          {t('Send')}
        </SendButton>
      </InputArea>
    </ChatPanelContainer>
  );
};

export default AIChatPanel;
