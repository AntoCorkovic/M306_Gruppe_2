# PowerStream

## Softwareumfang
Entwerfen und Programmieren Sie eine Software welche:
Muss:
• sdat-Files einlesen kann
• ESL-Files einlesen kann
• Die Verbrauchswerte in Zählerstände umrechnen kann
• Die Daten in einem Verbrauchsdiagramm visualisieren kann
• Die Daten in einem Zählerstandsdiagramm visualisieren kann
• Die Daten als csv exportieren kann

## Programmier Tipps vom Bünzli
ID735 = Einspeisung
<br>
ID742 = Bezug



### Eckpunkte sdat-File
```ruby
<rsm:DocumentID>eslevu156407_BR2294_ID735</rsm:DocumentID>
```
> Die DocumentID ist die eindeutige Identifizierung des Zählers.
```ruby
<rsm:Interval>
<rsm:StartDateTime>2019-09-24T22:00:00Z</rsm:StartDateTime>
<rsm:EndDateTime>2019-09-25T22:00:00Z</rsm:EndDateTime>
</rsm:Interval>
```
> Innerhalb der Interval-Tags finden Sie Start und Endzeit in UTC der Zählerwerte.
```ruby
<rsm:Resolution>
<rsm:Resolution>15</rsm:Resolution>
<rsm:Unit>MIN</rsm:Unit>
</rsm:Resolution>
```
> Im Resolution-Tag steht die Auflösung (Zeitlicher Abstand der einzelnen Messwerte)
```ruby
<rsm:Observation>
  <rsm:Position>
    <rsm:Sequence>1</rsm:Sequence>
```
> Gibt die Nummer des Messwertes an.
```ruby
</rsm:Position>
<rsm:Volume>2.250</rsm:Volume>
```
> Gibt die gemessene Menge/Volumen innerhalb der letzten Resolution wieder
```ruby
<rsm:Condition>21</rsm:Condition>
</rsm:Observation>
```
> Am Ende des Files befinden sich mehrere Observation-Tags. Diese geben jeweils den Messwert im jeweiligen Zeitintervall an.



### Eckpunkte ESL-File

```ruby
<TimePeriod end="2019-01-01T00:00:00">
```
> Der Tag TimePeriod gibt an, von wann die Messwerte stammen.
```ruby
  <ValueRow obis="1-1:1.8.1" value="4755.3000" status="V"/>
  <ValueRow obis="1-1:1.8.2" value="14460.9000" status="V"/>
  <ValueRow obis="1-1:2.8.1" value="8258.1000" status="V"/>
  <ValueRow obis="1-1:2.8.2" value="3543.1000" status="V"/>
  <ValueRow obis="1-1:5.8.1" value="293.0000" status="V"/>
  <ValueRow obis="1-1:5.8.2" value="580.0000" status="V"/>
  <ValueRow obis="1-1:6.8.1" value="33.0000" status="V"/>
  <ValueRow obis="1-1:6.8.2" value="8.0000" status="V"/>
  <ValueRow obis="1-1:7.8.1" value="406.0000" status="V"/>
  <ValueRow obis="1-1:7.8.2" value="163.0000" status="V"/>
  <ValueRow obis="1-1:8.8.1" value="500.0000" status="V"/>
  <ValueRow obis="1-1:8.8.2" value="1685.0000" status="V"/>
```
> Pro Zähler, welcher über den obis-code identifiziert wird, gibt es einen value welcher für den Zählerstand zum Zeitpunkt in der TimePeriod steht.
```ruby
</TimePeriod>
```
















