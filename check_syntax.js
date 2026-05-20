var fs = require('fs');
var h = fs.readFileSync('golem.html', 'utf8');
var js = h.slice(h.indexOf('<script>') + 9, h.indexOf('</script>'));
try {
  new Function(js);
  console.log('JS syntax OK');
  process.exit(0);
} catch(e) {
  console.error('Syntax error:', e.message);
  process.exit(1);
}
