import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
  context.subscriptions.push(
    vscode.commands.registerCommand('trevixa.openChat', async () => {
      const panel = vscode.window.createWebviewPanel('trevixaChat', 'Trevixa Chat', vscode.ViewColumn.Beside, {
        enableScripts: true
      });

      panel.webview.html = `<!doctype html>
<html><body>
<h2>Trevixa Encode Chat</h2>
<textarea id="log" style="width:100%;height:70%"></textarea><br/>
<input id="prompt" style="width:80%"/><button onclick="send()">Send</button>
<script>
const log = document.getElementById('log');
const prompt = document.getElementById('prompt');
function send(){
  const text = prompt.value.trim();
  if(!text) return;
  log.value += `You: ${text}\nTrevixa: [local extension stub] ${text}\n\n`;
  prompt.value='';
}
</script>
</body></html>`;
    }),

    vscode.commands.registerCommand('trevixa.createFile', async () => {
      const fileName = await vscode.window.showInputBox({ prompt: 'File path to create' });
      if (!fileName) return;
      const uri = vscode.Uri.file(fileName);
      await vscode.workspace.fs.writeFile(uri, Buffer.from('', 'utf8'));
      vscode.window.showInformationMessage(`Created ${fileName}`);
    }),

    vscode.commands.registerCommand('trevixa.deleteFile', async () => {
      const fileName = await vscode.window.showInputBox({ prompt: 'File path to delete' });
      if (!fileName) return;
      const yes = await vscode.window.showWarningMessage(`Delete ${fileName}?`, 'Yes', 'No');
      if (yes !== 'Yes') return;
      await vscode.workspace.fs.delete(vscode.Uri.file(fileName));
      vscode.window.showInformationMessage(`Deleted ${fileName}`);
    }),

    vscode.commands.registerCommand('trevixa.applyPatch', async () => {
      const editor = vscode.window.activeTextEditor;
      if (!editor) return;
      const suggestion = await vscode.window.showInputBox({ prompt: 'Text to append as patch preview' });
      if (!suggestion) return;
      await editor.edit((builder) => builder.insert(new vscode.Position(editor.document.lineCount, 0), `\n${suggestion}\n`));
      vscode.window.showInformationMessage('Patch text inserted.');
    })
  );
}

export function deactivate() {}
