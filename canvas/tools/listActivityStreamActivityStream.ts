
import { tool } from "ai";
import { listActivityStreamActivityStreamDataSchema } from "./aitm.schema.ts";
import { listActivityStreamActivityStream, ListActivityStreamActivityStreamData } from "..";

export default tool({
  description: `
  List the activity stream
Returns the current user's global activity stream, paginated.

There are
many types of objects that can be returned in the activity
stream. All object types have the same
basic set of shared attributes:
!!!javascript
{
'created_at': '2011-07-13T09:12:00Z',
'updated_at':
'2011-07-25T08:52:41Z',
'id': 1234,
'title': 'Stream Item Subject',
'message': 'This is the body
text of the activity stream item. It is plain-text, and can be multiple paragraphs.',
'type':
'DiscussionTopic|Conversation|Message|Submission|Conference|Collaboration|AssessmentRequest...',
're
d_state': false,
'context_type': 'course', // course|group
'course_id': 1,
'group_id':
null,
'html_url': "http://..." // URL to the Canvas web UI for this stream item
}
In addition, each
item type has its own set of attributes available.
DiscussionTopic:
'type':
'DiscussionTopic',
'discussion_topic_id': 1234,
'total_root_discussion_entries':
5,
'require_initial_post': true,
'user_has_posted': true,
'root_discussion_entries': {
...
}
For
DiscussionTopic, the message is truncated at 4kb.
Announcement:
'type':
'Announcement',
'announcement_id': 1234,
'total_root_discussion_entries': 5,
'require_initial_post':
true,
'user_has_posted': null,
'root_discussion_entries': {
...
For Announcement, the message is
truncated at 4kb.
Conversation:
'type': 'Conversation',
'conversation_id': 1234,
'private':
false,
'participant_count': 3,
Message:
'type': 'Message',
'message_id':
1234,
'notification_category': 'Assignment Graded'
Submission:
Returns an
{api:Submissions:Submission Submission} with its Course and Assignment data.
Conference:
'type':
'Conference',
'web_conference_id': 1234
Collaboration:
'type': 'Collaboration',
'collaboration_id':
1234
AssessmentRequest:
'type': 'AssessmentRequest',
'assessment_request_id': 1234
    `,
  parameters: listActivityStreamActivityStreamDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListActivityStreamActivityStreamData, "url"> ) => {
    try {
      const { data } = await listActivityStreamActivityStream(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    