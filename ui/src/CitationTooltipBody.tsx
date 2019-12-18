import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import React from "react";
import Citation from "./Citation";
import FeedbackButton from "./FeedbackButton";
import { ScholarReaderContext } from "./state";
import * as api from "./types/api";

interface CitationTooltipBodyProps {
  paperIds: string[];
  citation: api.Citation;
}

export class CitationTooltipBody extends React.PureComponent<
  CitationTooltipBodyProps
> {
  render() {
    return (
      <div className="tooltip-body citation-tooltip-body">
        <div className="tooltip-body__section tooltip-body__label tooltip-body__header">
          <div className="tooltip-body__label">
            This citation was matched to {this.props.paperIds.length}
            {this.props.paperIds.length > 1 ? " papers" : " paper"}:
          </div>
          <FeedbackButton extraContext={{ citationId: this.props.citation.id }} />
        </div>
        <div className="tooltip-body__section">
          <List aria-label="cited papers">
            <ScholarReaderContext.Consumer>
              {({ setDrawerState, setJumpPaperId, setSelectedCitation }) => {
                return this.props.paperIds.map(s2Id => (
                  <ListItem
                    disableGutters
                    key={s2Id}
                    button
                    className="tooltip-body__citation"
                    onClick={() => {
                      setSelectedCitation(this.props.citation);
                      setDrawerState("show-citations");
                      setJumpPaperId(s2Id);
                    }}
                  >
                    <Citation key={s2Id} paperId={s2Id} />
                  </ListItem>
                ));
              }}
            </ScholarReaderContext.Consumer>
          </List>
        </div>
      </div>
    );
  }
}

export default CitationTooltipBody;
